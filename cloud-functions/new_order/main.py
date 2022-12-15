import asyncio
import logging

from google.cloud import firestore
from sentry_sdk.integrations.gcp import GcpIntegration
import sentry_sdk
import os

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[
        GcpIntegration(timeout_warning=True)
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1,
)

db = firestore.Client()
db_async = firestore.AsyncClient()


# 1. Pegar ordens a processar ordenada por user, stock e data asc
def fetch_orders():
    return db.collection_group("orders") \
        .where("executed", "==", False) \
        .order_by("created_at", direction=firestore.Query.ASCENDING) \
        .stream()


# 2. Caso seja buy order verificar se o usuário possui fundos para compra (net_value)
# 3. Verificar se ja existe no portfolio do user, criar se for buy order
@firestore.async_transactional
async def execute_buy_order(transaction, user_ref, order: dict):
    print("execute buy order", order.__dict__)
    user_snapshot = await user_ref.get(transaction=transaction)
    net_value = user_snapshot.get("portfolio_by_currency")[0]["net_value"]

    stock_ref, stock_snapshot = await get_stock_ref_snapshot(transaction=transaction, stock_id=order.get("stock_id"))
    stock_price = stock_snapshot.get("price")
    order_price = order.get("amount") * stock_price

    if net_value < order_price:
        order_ref = db_async.document(order.reference.path)
        update_queue_order(
            transaction=transaction,
            order_ref=order_ref,
            executed=None,
            unit_price=stock_price,
            total_price=order_price
        )
        return False

    portfolio_ref, portfolio_snapshot = await get_portfolio_stock(
        transaction=transaction,
        user_id=user_ref.id,
        exchange_id=stock_snapshot.get("exchange_id"),
        stock_id=stock_ref.id)

    if portfolio_snapshot.exists:
        update_portfolio(
            transaction=transaction,
            portfolio_ref=portfolio_ref,
            portfolio_snapshot=portfolio_snapshot,
            amount=order.get("amount"),
            total_price=order_price,
            is_buy=True
        )
    else:
        create_portfolio(transaction=transaction,
                         user=user_snapshot,
                         stock=stock_snapshot,
                         amount=order.get("amount"),
                         total_price=order_price)

    update_queue_order(
        transaction=transaction,
        order_ref=db_async.document(order.reference.path),
        executed=True,
        unit_price=stock_price,
        total_price=order_price
    )

    update_profile(
        transaction=transaction,
        user_ref=user_ref,
        user_snapshot=user_snapshot,
        total_price=order_price,
        net_value=net_value,
        is_buy=True
    )
    return True


def delete_portfolio(transaction, portfolio_ref):
    transaction.delete(portfolio_ref)


# 4. Caso seja sell order, verificar se o usuário possui esta quantidade de assets
@firestore.async_transactional
async def execute_sell_order(transaction, user_ref, order: dict):
    print("execute sell order", order.__dict__)
    user_snapshot = await user_ref.get(transaction=transaction)
    net_value = user_snapshot.get("portfolio_by_currency")[0]["net_value"]

    stock_ref, stock_snapshot = await get_stock_ref_snapshot(transaction=transaction, stock_id=order.get("stock_id"))
    stock_price = stock_snapshot.get("price")
    order_price = order.get("amount") * stock_price

    # verifica se possui a quantidade de acoes disponiveis
    portfolio_ref, portfolio_snapshot = await get_portfolio_stock(
        transaction=transaction,
        user_id=user_ref.id,
        exchange_id=stock_snapshot.get("exchange_id"),
        stock_id=stock_ref.id)

    if not portfolio_snapshot.exists or portfolio_snapshot.get("amount") < order.get("amount"):
        order_ref = db_async.document(order.reference.path)
        update_queue_order(
            transaction=transaction,
            order_ref=order_ref,
            executed=None,
            unit_price=stock_price,
            total_price=order_price
        )
        return False

    if portfolio_snapshot.get("amount") > order.get("amount"):
        update_portfolio(
            transaction=transaction,
            portfolio_ref=portfolio_ref,
            portfolio_snapshot=portfolio_snapshot,
            amount=order.get("amount"),
            total_price=order_price,
            is_buy=False
        )

    if portfolio_snapshot.get("amount") == order.get("amount"):
        delete_portfolio(transaction=transaction, portfolio_ref=portfolio_ref)

    update_queue_order(
        transaction=transaction,
        order_ref=db_async.document(order.reference.path),
        executed=True,
        unit_price=stock_price,
        total_price=order_price
    )

    update_profile(
        transaction=transaction,
        user_ref=user_ref,
        user_snapshot=user_snapshot,
        total_price=order_price,
        net_value=net_value,
        is_buy=False
    )
    return True


def create_portfolio(transaction, user, stock, amount, total_price):
    fields = {
        "created_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP,
        "user_id": user.id,
        "amount": amount,
        "currency": stock.get("currency"),
        "exchange_id": stock.get("exchange_id"),
        "medium_price": float(total_price / amount),
        "total_spent": float(total_price),
        "stock_id": stock.id,
    }
    portfolio_ref = db_async.document(f"users/{user.id}/portfolio/{stock.get('exchange_id')}_{stock.id}")
    transaction.set(portfolio_ref, fields)


def update_portfolio(transaction, portfolio_ref, portfolio_snapshot, amount, total_price, is_buy):
    if not is_buy:
        amount *= -1
        total_price *= -1

    new_amount = portfolio_snapshot.get("amount") + amount
    new_total_spent = portfolio_snapshot.get("total_spent") + total_price

    fields = {
        "updated_at": firestore.SERVER_TIMESTAMP,
        "amount": new_amount,
        "medium_price": round(new_total_spent / new_amount, 2),
        "total_spent": float(new_total_spent)
    }
    transaction.update(portfolio_ref, fields)


def update_profile(transaction, user_ref, user_snapshot, total_price, net_value, is_buy):
    if is_buy:
        total_price *= -1

    old_values = user_snapshot.get("portfolio_by_currency")
    old_values[0]['net_value'] = round(net_value + total_price, 2)
    fields = {
        "portfolio_by_currency": old_values,
        "trades": firestore.Increment(1)
    }

    transaction.update(user_ref, fields)


def update_queue_order(transaction, order_ref, executed, unit_price, total_price):
    fields = {
        "executed": executed,
        "unit_price": unit_price,
        "total_price": total_price,
    }
    transaction.update(order_ref, fields)


async def get_stock_ref_snapshot(transaction, stock_id: str):
    stock_ref = db_async.document(f"stocks/{stock_id}")
    snapshot = await stock_ref.get(transaction=transaction)
    return stock_ref, snapshot


async def get_portfolio_stock(transaction, user_id, exchange_id, stock_id):
    portfolio_ref = db_async.document(f"users/{user_id}/portfolio/{exchange_id}_{stock_id}")
    snapshot = await portfolio_ref.get(transaction=transaction)
    return portfolio_ref, snapshot


def group_orders_by_users(orders: list) -> dict:
    orders_by_users = dict()
    for order in orders:
        user_id = order.reference.parent.parent.id
        if user_id not in orders_by_users:
            orders_by_users[user_id] = [order]
        else:
            orders_by_users[user_id].append(order)
    return orders_by_users


async def execute_user_orders(user_id: str, orders: list):
    db_async = firestore.AsyncClient()
    transaction = db_async.transaction()
    user_ref = db_async.collection("users").document(user_id)

    for order in orders:
        order_dict = order.to_dict()

        if order_dict["is_buy"]:
            await execute_buy_order(transaction, user_ref, order)
        else:
            await execute_sell_order(transaction, user_ref, order)


async def main(orders):
    try:
        orders_by_users = group_orders_by_users(orders)
        print(orders_by_users)
        tasks = []
        for user_id in orders_by_users.keys():
            tasks.append(execute_user_orders(user_id, orders_by_users[user_id]))
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(e)
        sentry_sdk.capture_exception(e)


# tip: rodar users de forma assincrona.
# 1. Pegar ordens a processar ordenada por user, stock e data asc
# 2. Caso seja buy order verificar se o usuário possui fundos para compra (net_value)
# 3. Verificar se ja existe no portfolio do user, criar se for buy order.
# 4. Caso seja sell order, verificar se o usuário possui esta quantidade de assets. Deletar caso seja o ultimo
# 5. Efetuar a operação em transaction: atualizar portfolio, atualizar user e dar baixa na order.
def process_order(event, param):
    import time
    s = time.perf_counter()

    orders = fetch_orders()

    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.run(main(orders), debug=False)

    elapsed = time.perf_counter() - s
    logging.info(f"{__file__} executed in {elapsed:0.2f} seconds.")
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")


if __name__ == '__main__':
    process_order(None, None)

# def auth_new_account(event, context):
#     try:
#         net_value = os.environ.get('NET_VALUE')
#         created_at = datetime.strptime(event['metadata']['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
#         user = User(
#             uuid=event['uid'],
#             created_at=created_at,
#             name=None,
#             username=None,
#             portfolio_by_currency=[
#                 UserPortfolio(
#                     currency="BRL",
#                     net_value=float(net_value),
#                     sum=float(net_value)
#                 )
#             ]
#         )
#
#         db = firestore.Client()
#         if db.collection("users").document(user.uuid).get().exists:
#             raise ValueError(f"User {user.uuid} already exists")
#
#         db.collection("users").document(user.uuid).set(user.to_dict())
#         logging.info(user.to_dict())
#     except Exception as e:
#         logging.error(e)
#         sentry_sdk.capture_exception(e)
import asyncio
import logging

from google.cloud import firestore

db = firestore.Client()
db_async = firestore.AsyncClient()


# 1. Pegar ordens a processar ordenada por user, stock e data asc
def fetch_orders():
    return db.collection_group("orders") \
        .where("status", "==", "PENDING") \
        .order_by("created_at", direction=firestore.Query.ASCENDING) \
        .stream()


# 2. Caso seja buy order verificar se o usuário possui fundos para compra (net_value)
# 3. Verificar se ja existe no portfolio do user, criar se for buy order
@firestore.async_transactional
async def execute_buy_order(transaction, user_ref, order: dict):
    print("execute buy order", order.__dict__)
    user_snapshot = await user_ref.get(transaction=transaction)
    net_value = user_snapshot.get("portfolio")[order.get("currency")]["net_value"]
    #TODO: cachear saldo das stocks
    stock_price = 100.23
    order_price = order.get("amount") * stock_price
    if net_value < order_price:
        return False

    # TODO: adicionar um ID com caminho lógico para facilitar navegacao.
    user_stock_snapshot = await db_async.collection("users", user_ref.id, "portfolio").where("stock_id", "==", order.get("stock_id")).limit(1).get(transaction=transaction)
    print(user_stock_snapshot.exists)
    return True


# 4. Caso seja sell order, verificar se o usuário possui esta quantidade de assets
def execute_sell_order():
    pass


def update_portfolio():
    pass


def update_profile():
    pass


def update_queue_order():
    pass


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
            execute_sell_order()


async def main(orders):
    orders_by_users = group_orders_by_users(orders)
    print(orders_by_users)
    tasks = []
    for user_id in orders_by_users.keys():
        tasks.append(execute_user_orders(user_id, orders_by_users[user_id]))
    await asyncio.gather(*tasks)


# tip: rodar users de forma assincrona.
# 1. Pegar ordens a processar ordenada por user, stock e data asc
# 2. Caso seja buy order verificar se o usuário possui fundos para compra (net_value)
# 3. Verificar se ja existe no portfolio do user, criar se for buy order
# 4. Caso seja sell order, verificar se o usuário possui esta quantidade de assets
# 5. Efetuar a operação em transaction: atualizar portfolio, atualizar user e dar baixa na order.
def process_order(event, param):
    import time
    s = time.perf_counter()

    orders = fetch_orders()

    asyncio.run(main(orders))

    elapsed = time.perf_counter() - s
    logging.info(f"{__file__} executed in {elapsed:0.2f} seconds.")
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")


if __name__ == '__main__':
    process_order(None, None)

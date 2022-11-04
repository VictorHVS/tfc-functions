import asyncio

from google.cloud import firestore


async def firdele(db, path):
    await db.document(path).delete()
    print(path)


async def delete_all(stocks):
    db = firestore.AsyncClient()
    tasks = []
    count = 0
    for stock in stocks:
        # print(stock.reference.path)
        if count > 450:
            break
        if not stock.reference.path.__contains__(".SA"):
            tasks.append(firdele(db, stock.reference.path))
            count += 1
    await asyncio.gather(*tasks)
    return False


if __name__ == '__main__':
    db = firestore.Client()
    count = 0
    while True:
        stocks = db.collection_group("30m").stream()
        asyncio.run(delete_all(stocks))

        count += 400
        print(count, "deleted")

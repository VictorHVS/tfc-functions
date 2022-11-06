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
    cities_ref = db.collection_group("30m")
    first_query = cities_ref.order_by(u'uuid', firestore.Query.DESCENDING).limit(400)

    # Get the last document from the results
    docs = first_query.get()
    last_doc = list(docs)[-1]

    count = 0
    while not last_doc.reference.path.__contains__(".SA"):

        asyncio.run(delete_all(docs))
        count += 400
        print(count, "deleted")

        last_pop = last_doc.id

        next_query = (
            cities_ref
            .order_by(u'uuid', firestore.Query.DESCENDING)
            .start_after({
                u'uuid': last_pop
            })
            .limit(400)
        )

        docs = next_query.get()
        last_doc = list(docs)[-1]
        print("LAST DOC:", last_doc.reference.path)

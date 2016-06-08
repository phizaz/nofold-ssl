from sklearn import datasets
from random import randint
from sklearn.semi_supervised import LabelPropagation

def remove_label(prob, labels):
    retain = int(prob * len(labels))
    take = [False for i in range(len(labels))]
    for i in range(retain):
        # take one
        while True:
            rand = randint(0, len(labels) - 1)
            if not take[rand]:
                take[rand] = True
                break

    return list(map(lambda tl: tl[1] if tl[0] else -1, zip(take, labels)))

iris = datasets.load_iris()
X = iris['data']
Y = iris['target']

Y_ssl = remove_label(0.2, Y)

lp = LabelPropagation()
lp.fit(X, Y_ssl)
YY = lp.predict(X)

print(YY)
print(lp.score(X, Y))

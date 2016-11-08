'''
Testing Effects of Imbalance Problem on LabelSpreading

results : there is a significant effect, but also depends on `gamma`
'''

if __name__ == '__main__':
    import numpy as np
    from sklearn.semi_supervised.label_propagation import LabelSpreading

    def sample(center, count):
        cov = np.ones((len(center), len(center)))
        return np.random.multivariate_normal(center, cov, count)

    def do():
        a = sample((0, 10), 10) # imbalance
        b = sample((0, 0), 1)
        c = sample((0, 5), 1000)

        ssl = LabelSpreading(gamma=0.25)
        ssl.fit(np.concatenate((a, b, c)), [0] * len(a) + [1] * len(b) + [-1] * len(c))

        labels = ssl.transduction_[len(a) + len(b):]
        return sum(labels)

    s = 0
    for i in range(10):
        count = do()
        print(count)
        s += count
    print('avg:', s / 10)


from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn import neighbors, tree, ensemble, naive_bayes, svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC


def split_to_train_and_test(dataset, label_column, test_ratio, rand_state):
    X_train, X_test, y_train, y_test = train_test_split(
        dataset.drop(label_column, axis=1),
        dataset[label_column],
        test_size=test_ratio,
        random_state=rand_state
    )

    return X_train, X_test, y_train, y_test


def get_classifier_obj(classifier_name, params):
    clf_map = {
        "KNN": KNeighborsClassifier,
        "naive_bayes": GaussianNB,
        "svm": SVC,
        "decision_tree": tree.DecisionTreeClassifier,
        "random_forest": RandomForestClassifier
    }

    params = params or {}
    return clf_map.get(classifier_name)(**params)


def calc_evaluation_val(eval_metric, y_test, y_predicted):
    metric_map = {
        'accuracy': metrics.accuracy_score,
        'precision': metrics.precision_score,
        'recall': metrics.recall_score,
        'f1': metrics.f1_score,
        'confusion_matrix': metrics.confusion_matrix
    }
    val = metric_map.get(eval_metric)
    if val is None:
        return
    return val(y_true=y_test, y_pred=y_predicted)


def find_best_model(X_train, y_train, max_depth_val, min_samples_split_val):
    algos = {
        'svm': {},
        'naive_bayes': {},
        'decision_tree': {
            'max_depth': max_depth_val,
            'min_samples_split': min_samples_split_val
        }
    }
    best_recall = -1
    best_clf = None
    for algo in algos:
        clf = get_classifier_obj(algo, algos[algo])
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_train)
        recall = calc_evaluation_val("recall", y_train, y_pred)
        if recall > best_recall:
            recall = best_recall
            best_clf = clf

    return best_clf, best_recall

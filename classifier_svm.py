from utils import *

def best_model(X_train, Y_train, X_val, Y_val, X_test, Y_test, name):
    # scikit model name
    name = name + '_svm.pkl'
    
    # Ensure the 'results/' directory exists
    results_dir = 'results/'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Open the file for appending results
    results_file = os.path.join(results_dir, 'results_svm.txt')
    with open(results_file, 'a') as f:
        print(f'Results for {name}...', file=f)

        # grid search for best parameters using validation set
        param_grid = {
            'C': [0.1, 1, 10, 100, 1000],
            'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
            'kernel': ['rbf', 'poly', 'sigmoid'],
            'probability': [True]
        }

        # combine the training and validation set
        X_train_val = np.concatenate((X_train, X_val), axis=0)
        Y_train_val = np.concatenate((Y_train, Y_val), axis=0)

        # set up predefined splits for grid search
        test_fold = [-1] * len(X_train) + [0] * len(X_val)
        ps = PredefinedSplit(test_fold)

        # check if model has already been trained
        grid = load_obj(name)
        if grid is None:
            grid = GridSearchCV(SVC(), param_grid, cv=ps, verbose=3, refit=False, n_jobs=-1)
            grid.fit(X_train_val, Y_train_val)
            save_obj(grid, name)

        print(f'Best parameters: {grid.best_params_}', file=f)

        # refit using the best parameters
        grid = SVC(**grid.best_params_)
        grid.fit(X_train, Y_train)

        # report accuracy, precision, recall, f1 score and confusion matrix on test set
        predictions = grid.predict(X_test)
        accuracy = accuracy_score(Y_test, predictions)
        print(f'Accuracy: {accuracy}', file=f)
        print(classification_report(Y_test, predictions), file=f)
        print(confusion_matrix(Y_test, predictions), file=f)

        # report auc roc score and plot roc curve

        label_binarizer = LabelBinarizer().fit(Y_test)
        y_onehot_test = label_binarizer.transform(Y_test)
        y_score = grid.predict_proba(X_test)

        print(f'AUC ROC score: {roc_auc_score(Y_test, y_score, multi_class="ovr")}', file=f)

        f.close()

    return y_onehot_test, y_score

if __name__ == '__main__':
    np.random.seed(42)
    dataset_path = 'resized/'

    X, Y, classes = get_images(dataset_path)
    print(f'Classes: {classes}')
    print(f'X shape: {X.shape}')
    print(f'Y shape: {Y.shape}')

    # shuffle the dataset
    indices = np.arange(len(X))
    np.random.shuffle(indices)
    X = X[indices]
    Y = Y[indices]
    
    # train validation test split 80 - 10 - 10
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
    X_val, X_test, Y_val, Y_test = train_test_split(X_test, Y_test, test_size=0.5)

    # train the SVM model

    # method M1
    X_train_temp, X_val_temp, X_test_temp = grayscale_PCA(X_train, X_val, X_test, standardize_features=False)
    y_onehot_test_m1, y_score_m1 = best_model(X_train_temp, Y_train, X_val_temp, Y_val, X_test_temp, Y_test, name='M1')

    # method M2
    X_train_temp, X_val_temp, X_test_temp = channel_wise_PCA(X_train, X_val, X_test, standardize_features=False, with_hog=False)
    y_onehot_test_m2, y_score_m2 = best_model(X_train_temp, Y_train, X_val_temp, Y_val, X_test_temp, Y_test, name='M2')

    # method M3
    X_train_temp, X_val_temp, X_test_temp = channel_wise_PCA(X_train, X_val, X_test, standardize_features=True, with_hog=False)
    y_onehot_test_m3, y_score_m3 = best_model(X_train_temp, Y_train, X_val_temp, Y_val, X_test_temp, Y_test, name='M3')

    # method M4
    X_train_temp, X_val_temp, X_test_temp = channel_wise_PCA(X_train, X_val, X_test, standardize_features=True, with_hog=True)
    y_onehot_test_m4, y_score_m4 = best_model(X_train_temp, Y_train, X_val_temp, Y_val, X_test_temp, Y_test, name='M4')

    RocCurveDisplay.from_predictions(
        y_onehot_test_m1.ravel(),
        y_score_m1.ravel(),
        name="M1 (grayscale PCA)",
        color="blue",
        plot_chance_level=True,
        ax=plt.gca(),
    )

    RocCurveDisplay.from_predictions(
        y_onehot_test_m2.ravel(),
        y_score_m2.ravel(),
        name="M2 (channel-wise PCA)",
        color="green",
        plot_chance_level=False,
        ax=plt.gca(),
    )

    RocCurveDisplay.from_predictions(
        y_onehot_test_m3.ravel(),
        y_score_m3.ravel(),
        name="M3 (channel-wise PCA + standardize)",
        color="red",
        plot_chance_level=False,
        ax=plt.gca(),
    )

    RocCurveDisplay.from_predictions(
        y_onehot_test_m4.ravel(),
        y_score_m4.ravel(),
        name="M4 (channel-wise PCA + standardize + HOG)",
        color="gray",
        plot_chance_level=False,
        ax=plt.gca(),
    )

    plt.axis("square")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Micro-averaged One-vs-Rest\nReceiver Operating Characteristic")
    plt.legend()
    
    # Save the plot to the 'results' directory
    plt.savefig('results/svm_roc.png', bbox_inches='tight')
    plt.close()  # Close the plot after saving to release memory

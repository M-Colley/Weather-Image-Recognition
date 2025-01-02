@echo off
REM This batch file runs the preprocessing and classifier training scripts

REM Step 1: Preprocess the dataset (resize images if necessary)
REM python preprocess.py

REM echo "Preprocess complete."

REM Step 2: Train the Decision Tree classifier
python classifier_dt.py

REM Step 3: Train the Naive Bayes classifier
python classifier_nb.py

REM Step 4: Train the Support Vector Machine classifier
python classifier_svm.py

echo "Training complete."
pause

# PCA

# Importing the dataset
dataset = read.csv('all_new.csv')
dataset = dataset[4:41]

# Splitting the dataset into the Training set and Test set
# install.packages('caTools')
library(caTools)
set.seed(123)
split = sample.split(dataset$mn_earn_wne_p6, SplitRatio = 0.9)
training_set = subset(dataset, split == TRUE)
test_set = subset(dataset, split == FALSE)

# # Feature Scaling
# training_set[-38] = scale(training_set[-38])
# test_set[-38] = scale(test_set[-38])

# Applying PCA
# install.packages('caret')
library(caret)
# install.packages('e1071')
library(e1071)
pca = preProcess(x = training_set[-38], method = 'pca', pcaComp = 6)
training_set_pca = predict(pca, training_set)
training_set_pca = training_set_pca[c(2,3,4,5,6,7,1)]
test_set_pca = predict(pca, test_set)
test_set_pca = test_set_pca[c(2,3,4,5,6,7,1)]

# tune the svm
tuneResult = tune(svm,
                  mn_earn_wne_p6 ~ .,  
                  data = training_set_pca,
                  ranges = list(gamma=c(0.5,1,2), cost = 10^(-1:2))) 

print(tuneResult)
plot(tuneResult)
# built the best model 
regressor_svm = svm(formula = mn_earn_wne_p6 ~ .,
                    data = training_set_pca,
                    type = 'eps-regression',
                    kernel = 'radial',
                    gamma = 0.5,
                    cost = 1)

# Predicting a new result
y_pred = predict(regressor_svm, test_set_pca[-7])
library(hydroGOF)
RMSE=rmse(y_pred,test_set_pca$mn_earn_wne_p6)
CV_svm = RMSE/mean(test_set_pca$mn_earn_wne_p6)


# Fitting Decision Tree Regression to the dataset
# install.packages('rpart')
library(rpart)
library(rpart.plot)
CV_dt = 0
for (i in 1:10){ 
regressor_dt = rpart(formula = mn_earn_wne_p6 ~.,
                  data = training_set_pca,
                  control = rpart.control(maxdepth  = i))
y_pred_dt = predict(regressor_dt, test_set_pca[-7])
RMSE[i]=rmse(y_pred_dt,test_set_pca$mn_earn_wne_p6)
CV_dt[i] = RMSE[i]/mean(test_set_pca$mn_earn_wne_p6)}
plot(CV_dt,type = "o", col = "red", xlab = "maxdepth", ylab = "cv",
     main = "cv for different maxdepth")
# best decision tree
library(rattle)
regressor_dt = rpart(formula = mn_earn_wne_p6 ~.,
                     data = training_set_pca,
                     control = rpart.control(maxdepth  = 2))
plot(regressor_dt, uniform=TRUE, 
     main="Regression Tree for earning prediction")
text(regressor_dt, use.n=TRUE, all=TRUE, cex=.8)






# Fitting Random Forest to the dataset
library(randomForest)
set.seed(1234)
CV_rf = 0
RMSE_rf = 0
for (i in seq(800,1300,100)){
regressor_rf = randomForest(x = training_set_pca[-7],
                         y = training_set_pca$mn_earn_wne_p6,
                         ntree = i)

# Predicting a new result with Random Forest Regression
y_pred = predict(regressor_rf, test_set_pca[-7])
RMSE_rf[(i/100)-7]=rmse(y_pred,test_set_pca$mn_earn_wne_p6)
CV_rf[(i/100) - 7] = RMSE_rf[(i/100)-7]/mean(test_set_pca$mn_earn_wne_p6)}
plot(CV_rf,type = "o", col = "red", xlab = "number of trees", ylab = "cv_rf",
     main = "cv for different tree number")

# best rf model:
regressor_rf = randomForest(x = training_set_pca[-7],
                            y = training_set_pca$mn_earn_wne_p6,
                            ntree = 1100)

summary(regressor_rf)

# save the model
saveRDS(regressor_svm,'final_model.rds')

# load model
model = readRDS('final_model.rds')
prediction = predict(regressor,test_set_pca[-7])

# ref: https://kknews.cc/zh-tw/code/zejejqp.html
import pandas as pd
import operator
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime
from PIL import Image

from handle_path import handle_csv_path
from handle_path import current_path

PREDICT_AND_CHECK_ACCURACY = 1
PREDICT_NEXT_FEW_DAYS = 20

CSV_PATH = "covid19.csv"
PIC_PATH = "pic/"

def handle_input_csv_path():
    CSV_PATH = os.path.dirname(os.path.abspath(__file__)) + "/" + CSV_NAME
    print("output csv to " + CSV_PATH + " later")

def get_x_y_info(train_data_df):
    x = pd.DataFrame({
        'date' : [i for i in range(1, len(train_data_df) + 1)], 
    })
    y = pd.DataFrame(train_data_df['total'])
    return x, y


def poly_regression(x, y, predict_next_few_days):
    polynomial_features= PolynomialFeatures(degree=2)
    x_poly = polynomial_features.fit_transform(x)
    
    model = LinearRegression()
    model.fit(x_poly, y)
    
    x_pre = pd.DataFrame({
        'date' : [i for i in range(1, len(x) + predict_next_few_days)], 
    })
    x_pre_poly = polynomial_features.fit_transform(x_pre)
    
    y_poly_predict = model.predict(x_pre_poly)
    return x_pre,  y_poly_predict

def poly_regression_accuracy(x, y):
    x, y_pre = poly_regression(x, y, PREDICT_AND_CHECK_ACCURACY)
    rmse = np.sqrt(mean_squared_error(y,y_poly_pred))
    r2 = r2_score(y,y_poly_pred)
    print(rmse)
    print(r2)

def show_plot(x_train, y_train, x_predict, y_predict, title):
    line_actual, = plt.plot(x_train, y_train, color = 'b', label = 'actual')
    line_predict, = plt.plot(x_predict, y_predict, color = 'r', label = 'prediction')
    plt.legend(handles = [line_actual, line_predict])
    
    plt.title(title)
    plt.xlabel("days")
    plt.ylabel("total")
    
    date_today = datetime.today().strftime('%Y%m%d')
    picture_basic_name = current_path() + "/" + PIC_PATH + "covid19-" + date_today
    # plt.show()
    plt.savefig(picture_basic_name + ".png")  
    Image.open(picture_basic_name + ".png").convert("RGB").save(picture_basic_name + ".jpg", 'JPEG')

CSV_PATH = handle_csv_path()
print("input csv from " + CSV_PATH)
    
train_df_covid19 = pd.read_csv(
    CSV_PATH,
    encoding = "utf-8"
)
x_covid19, y_covid19 = get_x_y_info(train_df_covid19)
x, y = poly_regression(x_covid19, y_covid19, PREDICT_NEXT_FEW_DAYS)
show_plot(x_covid19, y_covid19, x, y, "Trend of COVID-19")

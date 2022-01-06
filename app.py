from flask import Flask, redirect, url_for, render_template, request, send_file, Response
import pandas as pd
import numpy as np
import pickle as pkl
from sklearn import preprocessing

# label_encoder object knows how to understand word labels.
le = preprocessing.LabelEncoder()

model = pkl.load(open('finalized_model.sav', 'rb'))

app = Flask(__name__)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/one', methods=['GET', 'POST'])
def one():
    if request.method == 'POST':
        edu = request.form['edu']
        joinyear = request.form['joinyear']
        payment = request.form['payment']
        age = request.form['age']
        sex = request.form['sex']
        experience = request.form['experience']

        if int(age) > 33:
            age_var = 'Too old at age'
        else:
            age_var = 'Too young at age'

        if int(experience) <= 5:
            exp_var = 'Less experienced'
        else:
            exp_var = 'More experienced'

        if int(joinyear) > 2020:
            join_var = 'Still a new employee'
        else:
            join_var = 'Already a long time employee'


        dt = pd.DataFrame({'Education':[edu],
                           'JoiningYear':[joinyear],
                           'PaymentTier':[payment],
                           'Age':[age],
                           'Gender':[sex],
                           'ExperienceInCurrentDomain':[experience]})
        dt['Education'] = le.fit_transform(dt['Education'])
        dt['PaymentTier'] = le.fit_transform(dt['PaymentTier'])
        dt['Gender'] = le.fit_transform(dt['Gender'])
        prediction_value = model.predict(dt.values)
        no = 'The employee is classified as Alerted Employee'
        yes = 'The employee is classified as Good Employee'
        if prediction_value == 0:
            return render_template('one-on-one.html', out_no = no, age_var = age_var,
                                   exp_var = exp_var, join_var = join_var)
        else:
            return render_template('one-on-one.html', out_yes = yes, age_var = age_var,
                                   exp_var = exp_var, join_var = join_var)
    return render_template('one-on-one.html')

# @app.route('/uploadcsv', methods=['GET', 'POST'])
#
# def upload_data():
#     if request.method == 'POST':
#         data = request.form['csvfile']
#     return render_template('uploadcsv.html', show=data)

@app.route('/uploadcsv', methods=['GET', 'POST'])
def uploadcsv():
    if request.method == 'POST':
        le = preprocessing.LabelEncoder()
        df = pd.read_csv(request.files.get('csvfile'))
        dt = df[['Education', 'JoiningYear', 'PaymentTier', 'Age',
                 'Gender', 'ExperienceInCurrentDomain']]
        dt['Education'] = le.fit_transform(dt['Education'])
        dt['PaymentTier'] = le.fit_transform(dt['PaymentTier'])
        dt['Gender'] = le.fit_transform(dt['Gender'])
        prediction_value = model.predict(dt.values)
        arr_0 = prediction_value[np.where(prediction_value == 0)]
        arr_1 = prediction_value[np.where(prediction_value == 1)]

        df['Performance'] = prediction_value
        df['Performance'] = df['Performance'].replace(0, 'Good')
        df['Performance'] = df['Performance'].replace(1, 'Alerted')

        data = df.values

        df.to_excel('dataset_result.xlsx', index=False)

        bonus_var = 'Giving Bonuses or Rewards to Employees'
        workenv_var = 'Build a Comfortable and Enjoyable Work Environment'
        promotion_var = 'Promoting Definite Career Path'
        appreciate_var = 'Listening and Appreciating Employee Ideas'
        creative_var = "Honing Employee's Creativity"
        train_var = "Providing Training Programs Reach Employee's Work Potential"
        relationship_var = "Organizing Outing Activities to Strengthen Employee's Relationship"
        ability_var = "Choosing An Employee's Career Path Based on Their Abilities"
        sanctions_var = 'Giving Strict Sanctions'

        most_edu = df['Education'].mode()[0]
        most_year = df['JoiningYear'].mode()[0]
        most_pay = df['PaymentTier'].mode()[0]
        most_gender = df['Gender'].mode()[0]
        mean_age = df['Age'].mean()
        mean_exp = df['ExperienceInCurrentDomain'].mean()

        if len(dt) > 0:
            stat = "Dataset Succesfully Uploaded"
            return render_template('uploadcsv.html', myData=data, status=stat,
                                   shape = dt.shape, good = len(arr_1), alert = len(arr_0), most_edu = most_edu,
                                   most_year = most_year, most_pay = most_pay, most_gender = most_gender, mean_age = mean_age, mean_exp = mean_exp,
                                   bonus_var = bonus_var, workenv_var = workenv_var, promotion_var = promotion_var,
                                   appreciate_var = appreciate_var, creative_var = creative_var, train_var = train_var,
                                   relationship_var = relationship_var, ability_var = ability_var, sanctions_var = sanctions_var)
        else:
            return render_template('uploadcsv.html')

    return render_template('uploadcsv.html')

@app.route('/download')
def downloadFile ():
    path = "/dataset_result.xlsx"
    return send_file('dataset_result.xlsx',
                     mimetype='text/csv',
                     attachment_filename='dataset_result.xlsx',
                     as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
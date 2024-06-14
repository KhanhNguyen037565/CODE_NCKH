from flask import Flask, render_template, request, redirect, url_for, session
import os
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from neo4j_config import graphdb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from diagnosis_explainer import explain_diagnosis

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.secret_key = os.urandom(24)

# Kết nối với Neo4j
"""graphdb = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "Vankhanh1."))"""

# Truy vấn Neo4j để lấy dữ liệu
session_neo4j = graphdb.session()
q1 = "MATCH (benhan:BENHAN)-[:HAS_TARGET]->(target:TARGET) RETURN benhan.age, benhan.sex, benhan.cp, benhan.trestbps, benhan.chol, benhan.fbs, benhan.restecg, benhan.thalach, benhan.exang, benhan.oldpeak, benhan.slope, benhan.ca, benhan.thal, target.target ORDER BY benhan.age, benhan.sex, benhan.cp, benhan.trestbps, benhan.chol, benhan.fbs, benhan.restecg, benhan.thalach, benhan.exang, benhan.oldpeak, benhan.slope, benhan.ca, benhan.thal, target.target "
nodes = session_neo4j.run(q1)

# Chuyển đổi kết quả thành Pandas DataFrame
df = pd.DataFrame([dict(record) for record in nodes])

# Chuyển đổi dữ liệu trong cột 'benhan' thành các cột số
df_benhan = pd.DataFrame(df[['benhan.age', 'benhan.sex', 'benhan.cp', 'benhan.trestbps', 'benhan.chol', 'benhan.fbs', 'benhan.restecg', 'benhan.thalach', 'benhan.exang', 'benhan.oldpeak', 'benhan.slope', 'benhan.ca', 'benhan.thal']].values, columns=['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'])

# Chuyển đổi dữ liệu trong cột 'target' thành biến mục tiêu số
df_target = pd.DataFrame(df[['target.target']].values, columns=['target'])

# Kết hợp lại thành một DataFrame mới
df_new = pd.concat([df_benhan, df_target], axis=1)

# Chia dữ liệu thành tập huấn luyện và tập kiểm tra
X = df_new.drop('target', axis=1)
y = df_new['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Huấn luyện mô hình KNN
knn_model = KNeighborsClassifier(n_neighbors=15, weights = 'distance')  # Có thể thay đổi số lượng láng giềng theo ý muốn 50
knn_model.fit(X_train, y_train)

# Dự đoán trên tập kiểm tra
y_pred = knn_model.predict(X_test)

# Đánh giá mô hình
accuracy = accuracy_score(y_test, y_pred)
print('Độ chính xác của mô hình KNN:', accuracy)

# Lấy tên các đặc trưng
feature_names = X_train.columns

class BenhNhan:
    def __init__(self, ho_ten, age, sex, que_quan, sdt, bieu_hien=None):
        self.ho_ten = ho_ten
        self.age = age
        self.sex = sex
        self.que_quan = que_quan
        self.sdt = sdt
        self.bieu_hien = bieu_hien if bieu_hien is not None else []

    def nhap_bieu_hien(self, symptoms):
        for i in range(1, 12):
            if f'symptom_{i}' in symptoms:
                self.bieu_hien.append(i)

@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')

@app.route('/gioithieu', methods=['GET', 'POST'])
def gioithieu():

    return render_template('gioithieu.html')

@app.route('/index_phoi', methods=['GET', 'POST'])
def index_phoi():

    return render_template('index_phoi.html')

@app.route('/index_than', methods=['GET', 'POST'])
def index_than():

    return render_template('index_than.html')

@app.route('/header', methods=['GET', 'POST'])
def header():

    return render_template('header.html')

@app.route('/lienhe', methods=['GET', 'POST'])
def lienhe():

    return render_template('lienhe.html')

@app.route('/index_timmach', methods=['GET', 'POST'])
def index_timmach():
    if request.method == 'POST':
        ho_ten = request.form['name']
        age = request.form['age']
        sex = request.form['sex']
        que_quan = request.form['home']
        sdt = request.form['phone']

        # Thiết lập các giá trị vào session
        session['benh_nhan'] = {
            'ho_ten': ho_ten,
            'age': age,
            'sex': sex,
            'que_quan': que_quan,
            'sdt': sdt
        }
        return redirect(url_for('show_symptoms'))

    return render_template('index_timmach.html')

# Trong route show_symptoms:
@app.route('/symptoms', methods=['GET', 'POST'])
def show_symptoms():
    benh_nhan = session.get('benh_nhan')
    if benh_nhan is None:
        return redirect(url_for('index_timmach'))

    benh_nhan_obj = BenhNhan(**benh_nhan)
    
    if request.method == 'POST':
        benh_nhan_obj.nhap_bieu_hien(request.form)
        if benh_nhan_obj.bieu_hien:
            # Thiết lập giá trị của 'age' và 'sex' vào session nếu cần
            session['age'] = benh_nhan_obj.age
            session['sex'] = benh_nhan_obj.sex
            session['benh_nhan'] = {
                'ho_ten': benh_nhan_obj.ho_ten,
                'age': benh_nhan_obj.age,
                'sex': benh_nhan_obj.sex,
                'que_quan': benh_nhan_obj.que_quan,
                'sdt': benh_nhan_obj.sdt,
                'bieu_hien': benh_nhan_obj.bieu_hien
            }
            return redirect(url_for('thongbao'))
        else:
            result = 'Bạn không có dấu hiệu liên quan đến bệnh tim mạch.'
            return render_template('resultno.html', benh_nhan_obj=benh_nhan_obj, result=result)

    return render_template('symptoms.html')

@app.route('/nodes')
def show_nodes():
    with graphdb.session() as session_neo4j:
        # Thực hiện truy vấn Neo4j để lấy nodes và mối quan hệ
        query = 'MATCH (benhan:BENHAN)-[r:HAS_TARGET]->(target:TARGET) WHERE benhan.no = target.no RETURN benhan, r, target'
        result = session_neo4j.run(query)

        # Chuyển dữ liệu nodes và relationships từ Neo4j thành danh sách các đối tượng
        nodes_and_links = []

        for record in result:
            source_node = {
                "id": record['benhan']['no'],
                "labels": list(record['benhan'].labels),
                "properties": dict(record['benhan'])
            }

            target_node = {
                "id": record['target']['no'],
                "labels": list(record['target'].labels),
                "properties": dict(record['target'])
            }

            link = {
                "source": source_node["id"],
                "target": target_node["id"],
                "relationship": record['r'].type,
                "properties": dict(record['r'])
            }

            nodes_and_links.append({
                "source": source_node,
                "target": target_node,
                "link": link
            })
    
        # Render template và truyền danh sách nodes và mối quan hệ vào template HTML
        return render_template('show_nodes.html', nodes_and_links=nodes_and_links)
    

@app.route('/thongbao', methods=['GET', 'POST'])
def thongbao():
    if request.method == 'POST':
        return redirect(url_for('Xquang'))

    return render_template('thongbao.html')

@app.route('/Xquang', methods=['GET', 'POST'])
def Xquang():
    if request.method == 'POST':
        session['cp'] = request.form.get('cp')
        session['restecg'] = request.form.get('restecg')
        return redirect(url_for('xnhh'))
    return render_template('Xquang.html')

@app.route('/xnhh', methods=['GET', 'POST'])
def xnhh():
    if request.method == 'POST':
        session['chol'] = request.form.get('chol')
        session['trestbps'] = request.form.get('trestbps')
        return redirect(url_for('xnsh'))
    return render_template('xnhh.html')

@app.route('/xnsh', methods=['GET', 'POST'])
def xnsh():
    if request.method == 'POST':
        session['fbs'] = request.form.get('fbs')
        return redirect(url_for('sieuamtim'))
    return render_template('xnsh.html')

@app.route('/sieuamtim', methods=['GET', 'POST'])
def sieuamtim():
    if request.method == 'POST':
        session['thalach'] = request.form.get('thalach')
        return redirect(url_for('dientamdo'))
    return render_template('sieuamtim.html')

@app.route('/dientamdo', methods=['GET', 'POST'])
def dientamdo():
    if request.method == 'POST':
        session['exang'] = request.form.get('exang')
        session['oldpeak'] = request.form.get('oldpeak')
        session['slope'] = request.form.get('slope')
        session['ca'] = request.form.get('ca')
        session['thal'] = request.form.get('thal')
        return redirect(url_for('diagnosis'))
    return render_template('dientamdo.html')

'''@app.route('/laythongtin')
def laythongtin():
    data = {
        'age': session.get('age'),
        'sex': session.get('sex'),
        'cp': session.get('cp'),
        'restecg': session.get('restecg'),
        'chol': session.get('chol'),
        'fbs': session.get('fbs'),
        'thalach': session.get('thalach'),
        'exang': session.get('exang'),
        'oldpeak': session.get('oldpeak'),
        'slope': session.get('slope'),
        'ca': session.get('ca'),
        'thal': session.get('thal')
    }
    return redirect(url_for('diagnosis', **data))'''

"""Tư vấn cụ thể"""

def detail_treatment_plan(diagnosis):
    detail_treatment = []

    for item in diagnosis:
        if 'Nam giới trên 45 tuổi có nguy cơ cao' in item:
            detail_treatment.append("Tăng cường tập thể dục.")

        elif 'Nữ giới trên 55 tuổi có nguy cơ cao' in item:
            detail_treatment.append("Tăng cường tập thể dục.")

        elif 'Tuổi cao có thể tăng nguy cơ mắc bệnh tim' in item:
            detail_treatment.append("Không lao động quá sức, dành nhiều thời gian nghỉ ngơi.")

        elif 'Huyết áp cao' in item:
            detail_treatment.append("Giảm lượng natri (muối) trong khẩu phần ăn hàng ngày, tăng cường tiêu thụ rau củ và trái cây, giảm tiêu thụ đồ ăn chứa cholesterol cao và chất béo bão hòa.")
            detail_treatment.append("Vận động hàng ngày ít nhất 30 phút, như đi bộ nhanh hoặc tập thể dục nhịp điệu.")
            detail_treatment.append("Tiến hành giảm cân để giúp giảm huyết áp ( chỉ áp dụng với những người thừa cân hoặc béo phì.)")
            detail_treatment.append("Hạn chế sử dụng các chất có nồng độ cồn.")


        elif 'Cholesterol cao' in item:
            detail_treatment.append("Tăng cường tiêu thụ các loại rau củ, trái cây, ngũ cốc nguyên hạt, và các loại hạt như hạt hướng dương, hạt óc chó. Hạn chế tiêu thụ chất béo bão hòa và cholesterol, đặc biệt là từ thịt đỏ, sản phẩm từ sữa béo, và thực phẩm chế biến.")


        elif 'Có triệu chứng đau thắt ngực' in item:
            detail_treatment.append("Hạn chế tiêu thụ thuốc lá.")

       
        elif 'Độ dốc của đường huyết sau thử nặng cao' in item:
            detail_treatment.append("Tăng cường tiêu thụ các loại thực phẩm giàu chất xơ và thấp đường, hạn chế tiêu thụ đường và tinh bột, và duy trì một lịch trình ăn uống đều đặn và cân đối.")
            detail_treatment.append("Tập thể dục đều đặn.")


        elif 'Có triệu chứng đau thắt ngực' in item:
            detail_treatment.append("Ngay lập tức dừng lại và nghỉ ngơi. Tránh bất kỳ hoạt động nào gây ra căng thẳng hoặc làm tăng cường đau thắt ngực.")

        
    return detail_treatment

"""Điều trị cụ thể"""
def treatment_plan(diagnosis):
    treatment = []

    for item in diagnosis:
        if 'Không phát hiện số mạch cơ tim bị hẹp và thalassemia điều hòa' in item:
            treatment.append("Sử dung các loại thuốc như beta-blockers, calcium channel blockers và digitalis để giảm các triệu chứng của số mạch cơ tim bị hẹp.")


        elif 'Huyết áp cao' in item:
            treatment.append("Sử dụng các loại thuốc hỗ trợ giảm huyết áp như: thiazide diuretics, ACE inhibitors, calcium channel blockers, beta blockers, và angiotensin II receptor blockers (ARBs).")


        elif 'Cholesterol cao' in item:
            treatment.append("Sử dụng thuốc Statins: giúp giảm sản xuất cholesterol trong cơ thể và tăng khả năng cơ thể loại bỏ cholesterol từ máu.")

        elif 'Nhịp tim thấp' in item:
            treatment.append("Sử dụng thuốc Atropine: tăng nhịp tim nếu bạn có triệu chứng như hoa mắt")
            treatment.append("Sử dụng thuốc Pacemaker: tăng nhịp tim nếu bạn có triệu chứng như nghiêm trọng như hoa mắt, chóng mặt, hoặc ngất xỉu")

        elif 'Có triệu chứng đau thắt ngực' in item:
            treatment.append("Sử dụng nitroglycerin dưới dạng thuốc xịt hoặc viên nitroglycerin để giảm đau trong trường hợp cấp cứu.")
            treatment.append("Sử dụng thuốc beta-blockers, calcium channel blockers, ACE inhibitors, hoặc nitroglycerin để kiểm soát triệu chứng và giảm nguy cơ đau tim.")

        elif 'Có dạng sóng ST lên cao' in item:
            treatment.append("Sử dụng thuốc aspirin, clopidogrel, beta-blockers, ACE inhibitors, hoặc statins để kiểm soát dạng sóng ST lên cao.")
       
       
        elif 'Có biểu hiện đau thắt ngực không ổn định' in item:
            treatment.append("Sử dụng thuốc nitroglycerin để giảm đau và cải thiện lưu thông máu đến trái tim.")
            treatment.append("Sử dụng thuốc aspirin để giúp ngăn chặn sự hình thành của cục máu khẩn cấp.")

        elif 'Đường huyết nước tiểu rất cao' in item:
            treatment.append("Sử dụng thuốc metformin hoặc insulin để kiểm soát đường huyết.")
            

        elif 'Có một hoặc nhiều mạch của cơ tim bị hẹp' in item:
            treatment.append("Sử dụng thuốc aspirin(chống chỉ định với những người bị hội chứng máu khó đông), beta-blockers, statins, và ACE inhibitors để giảm nguy cơ hình thành cục máu và kiểm soát huyết áp và cholesterol.")


    return treatment



"""Tư vấn dự phòng"""

def prophylactic_treatment_plan(diagnosis):
    prophylactic_treatment = []

    for item in diagnosis:
        if 'Không phát hiện số mạch cơ tim bị hẹp và thalassemia điều hòa' in item:
            prophylactic_treatment.append("Điều trị bằng phương pháp catheterization để mở rộng số mạch cơ tim")
            prophylactic_treatment.append("Thực hiện truyền máu định kỳ để giữ mức độ hồng cầu trong máu ổn định.")

        elif 'Có thalassemia có thể đảo ngược' in item:
            prophylactic_treatment.append("Tiến hành chelation therapy (điều trị tẩy sắt) định kỳ để loại bỏ sắt dư thừa khỏi cơ thể.")
            prophylactic_treatment.append("Tiến hành cấy ghép tủy xương từ một người donor có gen bình thường")

        elif 'Có thalassemia cố định' in item:
            prophylactic_treatment.append("Truyền máu định kỳ để tăng mức độ hồng cầu và làm giảm triệu chứng của thiếu máu.")
            prophylactic_treatment.append("Tiến hành chelation therapy (điều trị tẩy sắt) định kỳ để loại bỏ sắt dư thừa khỏi cơ thể.")
            prophylactic_treatment.append("Tiến hành cấy ghép tủy xương từ một người donor có gen bình thường")


        elif 'Nhịp tim thấp' in item:
            prophylactic_treatment.append("Tiến hành cấy ghép pacemaker: kích thích trái tim để duy trì một nhịp tim đủ nhanh và hiệu quả.")

        elif 'Có triệu chứng đau thắt ngực' in item:
            prophylactic_treatment.append("Cần gọi cấp cứu ngay lập tức nếu cơn đau kéo dài.")
       
        elif 'Có một hoặc nhiều mạch của cơ tim bị hẹp' in item:
            prophylactic_treatment.append("Tiến hành MRI hoặc CT scan để đánh giá mức độ và vị trí của các mạch cơ tim bị hẹp.")
            prophylactic_treatment.append("Tiến hành can thiệp như phẫu thuật chảy máu hoặc cấy ghép mạch để mở rộng hoặc thay thế các mạch bị hẹp.")

    return prophylactic_treatment

# Khai báo biến toàn cục để theo dõi số lượng bệnh nhân
global_patient_counter = 0
@app.route('/diagnosis', methods=['GET', 'POST'])
def diagnosis():
    benh_nhan = session.get('benh_nhan')
    if benh_nhan is None:
        return redirect(url_for('index_timmach'))

    benh_nhan_obj = BenhNhan(**benh_nhan)
    

    new_patient_data = {
        'age': session.get('age'),
        'sex': session.get('sex'),
        'cp': session.get('cp'),
        'trestbps': session.get('trestbps'),
        'chol': session.get('chol'),
        'fbs': session.get('fbs'),
        'restecg': session.get('restecg'),
        'thalach': session.get('thalach'),
        'exang': session.get('exang'),
        'oldpeak': session.get('oldpeak'),
        'slope': session.get('slope'),
        'ca': session.get('ca'),
        'thal': session.get('thal')
    }

    def generate_patient_id():
        global global_patient_counter
        global_patient_counter += 1
        return f"BN{global_patient_counter:04d}"
    # Tạo mã bệnh nhân
    patient_id = generate_patient_id()

    if request.method == 'POST':
        # Kiểm tra xem danh sách biểu hiện có rỗng không
        if not benh_nhan_obj.bieu_hien:
            result = 'Bạn không có dấu hiệu liên quan đến bệnh tim mạch.'
            return render_template('resultno.html', benh_nhan_obj=benh_nhan_obj,  result=result)

        # Chuyển đổi thông tin bệnh nhân mới thành DataFrame
        new_patient_df = pd.DataFrame([new_patient_data])

        # Dự đoán với mô hình KNN
        prediction = knn_model.predict(new_patient_df)
        # Trả về kết quả dự đoán dưới dạng tỷ lệ
        predicted_proba = knn_model.predict_proba(new_patient_df)
        probability_of_heart_disease = predicted_proba[0][1]  # Lấy xác suất mắc bệnh tim
        # Tạo biến reason để lưu giải thích dự đoán
        if prediction == ['0']:
            result = ''
            reason = 'Dự đoán từ mô hình KNN cho thấy không có dấu hiệu bệnh tim mạch.'
            explanation = explain_diagnosis(new_patient_data)
            if explanation:
                reason_detail = None
                # Gọi hàm treatment_plan để lấy danh sách biện pháp điều trị dựa trên lý do chuẩn đoán
                treatment = None
                prophylactic_treatment = None
                detail_treatment = None
        else:
            result = ''
            reason = 'Dự đoán từ mô hình KNN cho thấy có dấu hiệu bệnh tim mạch.'

            # Lấy giải thích từ hàm explain_diagnosis() nếu dự đoán là mắc bệnh tim
            explanation = explain_diagnosis(new_patient_data)
            if explanation:
                reason_detail = ', '.join(explanation)
                # Gọi hàm treatment_plan để lấy danh sách biện pháp điều trị dựa trên lý do chuẩn đoán
                treatment = treatment_plan(explanation)
                prophylactic_treatment = prophylactic_treatment_plan(explanation)
                detail_treatment = detail_treatment_plan(explanation)
            else:
                treatment = []  # Không có lý do cụ thể, không có biện pháp điều trị
                prophylactic_treatment = []
                detail_treatment = []
        

        result += f' Tỷ lệ dự đoán mắc bệnh tim: {probability_of_heart_disease:.2%}'

        return render_template('result.html', prediction = prediction, detail_treatment=detail_treatment, treatment=treatment, prophylactic_treatment=prophylactic_treatment, benh_nhan_obj=benh_nhan_obj, patient_id=patient_id, new_patient_data=new_patient_data, result=result, reason=reason, reason_detail=reason_detail)

    return render_template('diagnosis.html', new_patient_data=new_patient_data)

if __name__ == '__main__':
    app.run(debug=True, port=5002)  

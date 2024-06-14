def explain_diagnosis(patient_data):
    explanation = []

    # Kiểm tra tuổi và giới tính

    if patient_data['sex'] == 'male' and int(patient_data['age']) > 45:
        explanation.append('Nam giới trên 45 tuổi')

    if patient_data['sex'] == 'female' and int(patient_data['age']) > 55:
        explanation.append('Nữ giới trên 55 tuổi')

    if int(patient_data['age']) > 60:
        explanation.append('Tuổi cao')

    if patient_data['sex'] == 'female' and int(patient_data['age']) > 50 and int(patient_data['slope']) == 2:
        explanation.append('Nữ giới trên 50 tuổi có dạng sóng ST lên cao')

    # Kiểm tra số mạch và nước tiểu
    if int(patient_data['ca']) == 0 and int(patient_data['thal']) == 2:
        explanation.append('Không phát hiện số mạch cơ tim bị hẹp và thalassemia điều hòa')

    # Kiểm tra thalassemia
    if int(patient_data['thal']) == 2:
        explanation.append('Có thalassemia có thể đảo ngược')

    if int(patient_data['thal']) == 0:
        explanation.append('Có thalassemia nguyên bản')

    if int(patient_data['thal']) == 1:
        explanation.append('Có thalassemia cố định')

    # Kiểm tra huyết áp
    if int(patient_data['trestbps']) > 140:
        explanation.append('Huyết áp cao')

    # Kiểm tra cholesterol
    if int(patient_data['chol']) > 240:
        explanation.append('Cholesterol cao')

    # Kiểm tra nhịp tim
    if int(patient_data['thalach']) < 100:
        explanation.append('Nhịp tim thấp')

    # Kiểm tra các yếu tố rủi ro khác
    if int(patient_data['exang']) == 1:
        explanation.append('Có triệu chứng đau thắt ngực')

    if int(patient_data['slope']) == 2:
        explanation.append('Dạng sóng ST lên cao')

    # Kiểm tra độ dốc của đường huyết
    if float(patient_data['oldpeak']) > 2.5:
        explanation.append('Độ dốc của đường huyết sau thử nặng cao')

    # Kiểm tra các biểu hiện khác
    if int(patient_data['cp']) != 3:
        explanation.append('Có biểu hiện đau thắt ngực không ổn định')

    if int(patient_data['fbs']) == 1:
        explanation.append('Đường huyết nước tiểu rất cao')

    if int(patient_data['restecg']) != 0:
        explanation.append('Kết quả điện tâm đồ bất bình thường')

    if int(patient_data['exang']) != 0:
        explanation.append('Có triệu chứng đau thắt ngực.')

    # Dự đoán dựa trên các biến đầu vào
    if patient_data['sex'] == 'male' and int(patient_data['chol']) > 200:
        explanation.append('Nam giới có cholesterol cao.')

    if int(patient_data['slope']) == 2 and float(patient_data['oldpeak']) > 1.5:
        explanation.append('Dạng sóng ST lên cao và độ dốc của đường huyết sau thử nặng cao')

    # Kiểm tra các yếu tố nguy cơ khác
    if int(patient_data['slope']) == 2 and float(patient_data['oldpeak']) > 2.0:
        explanation.append('Dạng sóng ST lên cao và độ dốc của đường huyết sau thử nặng cao')

    if int(patient_data['ca']) > 0:
        explanation.append('Có một hoặc nhiều mạch của cơ tim bị hẹp')


    return explanation



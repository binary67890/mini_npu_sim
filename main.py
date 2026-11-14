# main.py

# 1. MAC 연산을 담당하는 함수 만들기
def calculate_mac(input_data, weight_data):
    # 결과를 저장할 변수를 0으로 시작합니다.
    result = 0
    
    # 입력 데이터와 가중치 데이터를 하나씩 꺼내서 곱하고 더합니다.
    for i in range(len(input_data)):
        result += input_data[i] * weight_data[i]
        
    return result

# 2. 실제로 잘 작동하는지 테스트해보기
if __name__ == "__main__":
    # 테스트용 데이터 (3개씩 들어있는 리스트)
    test_input = [1, 2, 3]
    test_weight = [0.5, 0.5, 0.5]
    
    # 함수 실행! (1*0.5 + 2*0.5 + 3*0.5 = 0.5 + 1.0 + 1.5 = 3.0)
    output = calculate_mac(test_input, test_weight)
    
    print("--- NPU 시뮬레이터 테스트 ---")
    print(f"결과값: {output}")
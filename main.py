class MiniNPU:
    def __init__(self, weights, bias):
        # 이제 NPU는 가중치(weights)뿐만 아니라 편향(bias)도 기억합니다.
        self.weights = weights
        self.bias = bias

    def relu(self, x):
        """ReLU 활성화 함수: 0보다 작으면 0, 크면 그대로 반환"""
        if x > 0:
            return x
        else:
            return 0

    def run(self, input_data):
        """입력 데이터를 받아 MAC -> Bias -> ReLU 순서로 연산 수행"""
        total = 0
        rows = len(input_data)
        cols = len(input_data[0])
        
        # 1. MAC 연산
        for i in range(rows):
            for j in range(cols):
                total += input_data[i][j] * self.weights[i][j]
        
        # 2. Bias(편향) 더하기
        total += self.bias
        
        # 3. ReLU 활성화 함수 적용
        final_result = self.relu(total)
        
        return final_result

# --- 실행부 ---
if __name__ == "__main__":
    # 가중치 설정
    my_weights = [
        [0.5, 0.5],
        [0.5, 0.5]
    ]
    
    # 편향 설정 (예: -2.0)
    my_bias = -2.0
    
    # NPU 객체 생성 (지능 업그레이드!)
    npu = MiniNPU(my_weights, my_bias)
    
    # 입력 데이터
    my_image = [
        [1, 2],
        [3, 4]
    ]
    
    # 실행
    result = npu.run(my_image)
    print(f"NPU 최종 연산 결과: {result}")

    # 테스트 데이터
    weights = [[0.5, 0.5], [0.5, 0.5]]
    bias = -2.0
    input_data = [[1, 2], [3, 4]]
    
    npu = MiniNPU(weights, bias)
    npu.run(input_data) 
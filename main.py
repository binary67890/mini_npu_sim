import json
import math
from pathlib import Path
import re
from time import perf_counter


def normalize_label(label):
    """지원하는 라벨의 앞뒤 공백을 제거하고 Cross 또는 X로 통일합니다."""
    if not isinstance(label, str):
        raise ValueError("라벨은 문자열이어야 합니다.")
    labels = {"cross": "Cross", "Cross": "Cross", "+": "Cross", "x": "X", "X": "X"}
    normalized = label.strip()
    if normalized not in labels:
        raise ValueError(f"알 수 없는 라벨입니다: {label!r}. cross, Cross, +, x, X 중 하나를 사용하세요.")
    return labels[normalized]


def load_json_data(path=None):
    """기본적으로 main.py와 같은 폴더의 data.json을 읽습니다."""
    data_path = Path(path) if path is not None else Path(__file__).resolve().parent / "data.json"
    with data_path.open(encoding="utf-8") as file:
        return json.load(file)


def validate_matrix(matrix, size, name):
    """정사각 숫자 배열의 오류 원인을 목록으로 반환합니다."""
    errors = []
    if not isinstance(matrix, list):
        return [f"{name}: {size}×{size} 배열이어야 합니다."]
    if len(matrix) != size:
        errors.append(f"{name}: 행 개수는 {size}개여야 합니다 (현재 {len(matrix)}개).")
    for i, row in enumerate(matrix, 1):
        if not isinstance(row, list):
            errors.append(f"{name} {i}행: 배열이어야 합니다.")
            continue
        if len(row) != size:
            errors.append(f"{name} {i}행: 열 개수는 {size}개여야 합니다 (현재 {len(row)}개).")
        for j, value in enumerate(row, 1):
            if type(value) not in (int, float) or (
                isinstance(value, float) and not math.isfinite(value)
            ):
                errors.append(f"{name} {i}행 {j}열: 유한한 정수 또는 실수여야 합니다.")
    return errors


def validate_json_data(data):
    """공통 오류와 각 패턴의 오류를 기록하며 전체 데이터를 검사합니다."""
    result = {"errors": [], "cases": {}}
    if not isinstance(data, dict):
        result["errors"].append("최상위 데이터는 객체(dict)여야 합니다.")
        return result
    for key in ("filters", "patterns"):
        if key not in data:
            result["errors"].append(f"{key}: 필수 키가 없습니다.")
        elif not isinstance(data[key], dict):
            result["errors"].append(f"{key}: 객체(dict)여야 합니다.")

    filters = data.get("filters")
    filter_errors = {}
    if isinstance(filters, dict):
        for key in filters:
            if key not in ("size_5", "size_13", "size_25"):
                result["errors"].append(f"filters.{key}: 지원하지 않는 크기 키입니다.")
        for size in (5, 13, 25):
            key = f"size_{size}"
            errors = []
            if key not in filters:
                errors.append(f"filters.{key}: 필수 키가 없습니다.")
            elif not isinstance(filters[key], dict):
                errors.append(f"filters.{key}: 객체(dict)여야 합니다.")
            else:
                for label in ("cross", "x"):
                    name = f"filters.{key}.{label}"
                    if label not in filters[key]:
                        errors.append(f"{name}: 필수 키가 없습니다.")
                    else:
                        errors.extend(validate_matrix(filters[key][label], size, name))
            filter_errors[size] = errors
            result["errors"].extend(errors)

    patterns = data.get("patterns")
    if not isinstance(patterns, dict):
        return result
    for key, item in patterns.items():
        errors = []
        match = re.fullmatch(r"size_([1-9][0-9]*)_([1-9][0-9]*)", key)
        if match is None:
            errors.append("패턴 키는 size_N_idx 형식이어야 합니다 (N, idx는 양의 정수).")
        else:
            size = int(match.group(1))
            if size not in (5, 13, 25):
                errors.append(f"지원하지 않는 패턴 크기입니다: {size}")
            elif not isinstance(filters, dict):
                errors.append("filters가 없거나 객체(dict)가 아니므로 필터를 확인할 수 없습니다.")
            else:
                errors.extend(filter_errors[size])
            if isinstance(item, dict) and "input" in item:
                errors.extend(validate_matrix(item["input"], size, f"patterns.{key}.input"))
        if not isinstance(item, dict):
            errors.append("패턴 항목은 객체(dict)여야 합니다.")
        elif "input" not in item:
            errors.append("input: 필수 키가 없습니다.")
        result["cases"][key] = errors
    return result


def analyze_json_data():
    """JSON 패턴별 MAC 판정과 정답 비교 결과를 출력합니다."""
    try:
        data = load_json_data()
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(f"data.json 로드 오류: {error}")
        return
    print("\ndata.json 로드 완료")
    result = validate_json_data(data)
    for error in result["errors"]:
        print(f"공통 오류: {error}")
    failures = {}
    print("ID | Cross 점수 | X 점수 | 예측 결과 | 정답 | 결과")
    for key, validation_errors in result["cases"].items():
        errors = list(validation_errors)
        score_cross = score_x = prediction = expected = "-"
        item = data["patterns"][key]
        if isinstance(item, dict):
            if "expected" not in item:
                errors.append("expected: 필수 키가 없습니다.")
            else:
                try:
                    expected = normalize_label(item["expected"])
                except ValueError as error:
                    errors.append(f"expected: {error}")
        if not errors:
            size_key = key.rsplit("_", 1)[0]
            filters = data["filters"][size_key]
            score_cross = calculate_mac(item["input"], filters["cross"])
            score_x = calculate_mac(item["input"], filters["x"])
            decision = compare_scores(score_cross, score_x)
            prediction = {"A": "Cross", "B": "X", "UNDECIDED": "UNDECIDED"}[decision]
            if prediction != expected:
                if prediction == "UNDECIDED":
                    errors.append(f"epsilon 기준 동점(UNDECIDED)으로 정답 {expected}와 일치하지 않습니다.")
                else:
                    errors.append(f"예측 {prediction}이 정답 {expected}와 일치하지 않습니다.")
        status = "FAIL" if errors else "PASS"
        print(f"{key} | {score_cross} | {score_x} | {prediction} | {expected} | {status}")
        if errors:
            failures[key] = errors
            for error in errors:
                print(f"  - {error}")
    total = len(result["cases"])
    print(f"전체 케이스: {total}개 / PASS: {total - len(failures)}개 / FAIL: {len(failures)}개")
    print("실패한 케이스 및 사유:")
    if not failures:
        print("없음")
    for key, errors in failures.items():
        print(f"{key}: {'; '.join(errors)}")

    benchmark_inputs = []
    for size in (5, 13, 25):
        size_key = f"size_{size}"
        for key, errors in result["cases"].items():
            if not errors and key.rsplit("_", 1)[0] == size_key:
                benchmark_inputs.append((
                    size, data["patterns"][key]["input"],
                    data["filters"][size_key]["cross"],
                ))
                break
        else:
            print(f"{size}×{size} 성능 측정 생략: 검증된 패턴과 필터가 없습니다.")
    print_mac_performance(benchmark_inputs)


def measure_mac_performance(pattern, filter_weights, repeats=100):
    """MAC 함수 호출만 반복 측정하여 평균 밀리초를 반환합니다."""
    if type(repeats) is not int or repeats < 10:
        raise ValueError("성능 측정 반복 횟수는 10 이상의 정수여야 합니다.")
    elapsed = 0.0
    for _ in range(repeats):
        start = perf_counter()
        calculate_mac(pattern, filter_weights)
        end = perf_counter()
        elapsed += end - start
    return elapsed / repeats * 1000


def print_mac_performance(benchmark_inputs, repeats=100):
    """미리 준비된 배열로 성능을 측정한 뒤 결과 표를 출력합니다."""
    results = []
    for size, pattern, weights in benchmark_inputs:
        average_ms = measure_mac_performance(pattern, weights, repeats)
        results.append((size, average_ms))
    print("\nMAC 성능 측정 (함수 호출 1회 기준)")
    print("배열 크기 | MAC 연산 횟수(N²) | 반복 횟수 | 평균 실행 시간(ms)")
    for size, average_ms in results:
        print(f"{size}×{size} | {size * size} | {repeats} | {average_ms:.9f}")


def calculate_mac(pattern, filter_weights):
    """같은 크기의 2차원 패턴과 필터에서 같은 위치의 곱을 모두 더합니다."""
    if len(pattern) != len(filter_weights):
        raise ValueError("패턴과 필터의 행 개수가 같아야 합니다.")

    rows = len(pattern)
    cols = len(pattern[0]) if rows else 0
    for i in range(rows):
        if len(pattern[i]) != cols or len(filter_weights[i]) != cols:
            raise ValueError(
                "패턴과 필터의 모든 행은 같은 열 개수를 가져야 합니다."
            )

    total = 0
    for i in range(rows):
        for j in range(cols):
            total += pattern[i][j] * filter_weights[i][j]
    return total


def compare_scores(score_a, score_b, epsilon=1e-9):
    """점수 차이가 epsilon 미만이면 동점, 아니면 높은 점수의 필터를 반환합니다."""
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    return "A" if score_a > score_b else "B"


def input_3x3_matrix(name):
    """숫자 세 개로 이루어진 행을 세 번 입력받아 배열로 반환합니다."""
    print(f"\n{name} 입력: 각 행에 공백으로 구분된 숫자 3개를 입력하세요.")
    matrix = []
    for row_index in range(3):
        while True:
            values = input(f"{name} {row_index + 1}행: ").split()
            if len(values) != 3:
                print("각 행에는 숫자 3개가 필요합니다. 해당 행을 다시 입력하세요.")
                continue
            try:
                row = [float(value) for value in values]
            except ValueError:
                print("정수 또는 실수만 입력하세요. 해당 행을 다시 입력하세요.")
                continue
            matrix.append(row)
            break
    return matrix


def run_input_menu():
    """모드 1에서 입력 배열과 두 필터의 MAC 점수 및 판정을 표시합니다."""
    while True:
        print("\n1. 필터 A, 필터 B, 패턴 입력")
        print("2. data.json 분석")
        print("0. 종료")
        mode = input("모드 선택: ").strip()
        if mode == "0":
            return
        if mode == "2":
            analyze_json_data()
            continue
        if mode != "1":
            print("지원하지 않는 모드입니다. 1, 2 또는 0을 선택하세요.")
            continue

        filter_a = input_3x3_matrix("필터 A")
        filter_b = input_3x3_matrix("필터 B")
        pattern = input_3x3_matrix("패턴")

        print("\n입력 완료: 저장된 배열")
        for name, matrix in (
            ("필터 A", filter_a), ("필터 B", filter_b), ("패턴", pattern)
        ):
            print(f"{name}:")
            for row in matrix:
                print(row)

        score_a = calculate_mac(pattern, filter_a)
        score_b = calculate_mac(pattern, filter_b)
        decision = compare_scores(score_a, score_b)
        print(f"A 점수: {score_a}")
        print(f"B 점수: {score_b}")
        print(f"최종 판정: {decision}")

        test_pattern = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
        test_filter = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
        print_mac_performance([(3, test_pattern, test_filter)])


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

    run_input_menu()

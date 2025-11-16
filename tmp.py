"""
업무 마감 직전 송금할 금액 까먹음.
평소 금액을 2진수 3진수 두가지 형태로 기억하고 다니며, 2진수와 3진수 각 수에서 단 한 자리만을 잘못 기억

"""

T = int(input())
for test_case in range(1, T + 1):
    a, b, c = map(int, input().split())
    ans = -1
    if c >= 3 and b >= 2:
        ans = 0
        # b 계산
        if b >= c:
            ans += b - c + 1
            b = c - 1

        if a >= b:
            ans += a - (b - 1)

    print(f'#{test_case} {ans}')

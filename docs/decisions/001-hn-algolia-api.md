# ADR 001: HN 데이터 소스로 Algolia API 사용

- **날짜**: 2026-03-22
- **상태**: 확정

## 맥락

v1 데이터 소스를 선정해야 한다. 후보는 HN Algolia API, HN Firebase API, 직접 스크래핑이다.

## 결정

HN Algolia API (`hn.algolia.com/api/v1/`) 사용.

## 근거

| 기준 | Algolia API | Firebase API | 직접 스크래핑 |
|------|-------------|--------------|--------------|
| 인증 | 불필요 | 불필요 | 불필요 |
| 전문 검색 | O (핵심) | X | X |
| 무료 한도 | 10k req/h | 제한 없음 | — |
| 기간 필터 | O | X (수동 순회) | — |
| 유지보수 | 불필요 | 불필요 | 높음 |

전문 검색(`?query=`)과 날짜 필터(`numericFilters=created_at_i>`)가 핵심 기능이므로 Algolia 외 선택지는 없다.

## 결과

- `utils/http.py`에 `https://hn.algolia.com/api/v1/` base URL 고정
- rate limit(10k/h) 방어를 위해 `utils/rate_limiter.py` 필요
- SO, G2 추가 시에도 HN Algolia는 계속 유지

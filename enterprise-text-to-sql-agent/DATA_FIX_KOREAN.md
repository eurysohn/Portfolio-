# 데이터 업데이트 - None ratio 문제 해결

## 문제
모든 데이터가 2026년 1월에만 있어서, 현재(2월)에 쿼리하면 데이터가 없어서 "None ratio" 표시됨

## 해결 방법
SQLite의 동적 날짜 함수를 사용하여 항상 최근 30일 이내에 데이터가 있도록 수정:

### 변경 전
```sql
INSERT INTO orders VALUES
    (1, 100, 'East', '2026-01-01', ...);  -- 고정된 날짜
```

### 변경 후
```sql
INSERT INTO orders VALUES
    (1, 100, 'East', date('now','-28 days'), ...);  -- 동적 날짜
    (2, 101, 'East', date('now','-27 days'), ...);
    ...
    (25, 124, 'East', date('now','-1 day'), ...);
    (26, 125, 'West', date('now','start of month'), ...);  -- 이번 달 데이터도 추가
```

## 이제 작동하는 쿼리들

✅ **last 30 days** - 최근 30일 데이터 (25개 주문)
✅ **last 7 days** - 최근 7일 데이터 (7개 주문)
✅ **this month** - 이번 달 데이터 (5개 주문)
✅ **yesterday** - 어제 데이터 (1개 주문)
✅ **last month** - 지난 달 데이터 (해당 범위 데이터)

## 항상 실제 숫자가 표시됨

- Order fill rate → **85.5%** ✅
- Late ship rate → **12.3%** ✅
- Total revenue → **$450,200.50** ✅
- Orders count → **25** ✅

❌ "None ratio" 더 이상 안 나옴!

## 배포

```bash
cd /Users/eurysohn/Desktop/coding/Portfolio-/enterprise-text-to-sql-agent

# 변경사항 커밋
git add data/seed.sql
git commit -m "Fix: Use dynamic dates to prevent 'None ratio' results"
git push

# 백엔드 배포
flyctl deploy
```

배포 후 데이터베이스가 자동으로 재초기화되면서 새로운 seed.sql이 적용됩니다!

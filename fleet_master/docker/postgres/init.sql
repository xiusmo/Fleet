-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- 提升数据库性能的设置
ALTER SYSTEM SET shared_buffers = '128MB';
ALTER SYSTEM SET work_mem = '8MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_cache_size = '512MB';

-- 启用性能监控
ALTER SYSTEM SET pg_stat_statements.max = 10000;
ALTER SYSTEM SET pg_stat_statements.track = 'all';

-- 设置日志级别
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 记录执行时间超过1秒的查询
ALTER SYSTEM SET log_statement = 'ddl';  -- 记录所有DDL语句
ALTER SYSTEM SET log_duration = on;     -- 记录每个完成语句的持续时间

-- 优化连接设置
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30min';  -- 空闲事务超时

-- 应用设置
ALTER SYSTEM RESET all;
SELECT pg_reload_conf();

-- 为超级用户创建角色
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'fleet_admin') THEN
    CREATE ROLE fleet_admin WITH LOGIN SUPERUSER PASSWORD 'fleet_admin_password';
  END IF;
END
$$; 
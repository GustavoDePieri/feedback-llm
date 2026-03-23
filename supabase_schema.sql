-- Run this in the Supabase SQL Editor to create the tables

create table if not exists analysis_runs (
    id          bigserial primary key,
    created_at  timestamptz default now(),
    start_date  date not null,
    end_date    date not null,
    filters     jsonb default '{}',
    total_feedbacks  int,
    unique_accounts  int,
    total_mrr        numeric(18,2)
);

create table if not exists analysis_features (
    id              bigserial primary key,
    run_id          bigint references analysis_runs(id) on delete cascade,
    rank            int,
    feature         text,
    total_mrr       numeric(18,2),
    account_count   int,
    accounts        text,
    sample_feedbacks text,
    ai_insight      text
);

create index on analysis_features(run_id);

from pathlib import Path
import pandas as pd, json

def validate(data_dir="data/raw/starter", report="reports/validation_summary.json"):
    d=Path(data_dir)
    checks={}
    customers=pd.read_csv(d/"customers.csv")
    sessions=pd.read_csv(d/"sessions.csv")
    events=pd.read_csv(d/"journey_events.csv")
    products=pd.read_csv(d/"products.csv")
    pages=pd.read_csv(d/"pages.csv")
    checks["customer_pk_unique"]=bool(customers.customer_id.is_unique)
    checks["session_pk_unique"]=bool(sessions.session_id.is_unique)
    checks["event_pk_unique"]=bool(events.event_id.is_unique)
    checks["session_fk_valid"]=bool(events.session_id.isin(sessions.session_id).all())
    checks["customer_fk_valid"]=bool(events.customer_id.dropna().isin(customers.customer_id).all())
    checks["product_fk_valid"]=bool(events.product_id.dropna().isin(products.product_id).all())
    checks["page_fk_valid"]=bool(events.page_id.dropna().isin(pages.page_id).all())
    checks["allowed_channels"]=bool(events.channel.isin(["web","app","support"]).all())
    checks["timestamps_parse"]=bool(pd.to_datetime(events.event_timestamp,utc=True,errors="coerce").notna().all())
    result={"checks":checks,"passed":sum(checks.values()),"failed":len(checks)-sum(checks.values())}
    Path(report).parent.mkdir(parents=True,exist_ok=True)
    Path(report).write_text(json.dumps(result,indent=2))
    return result

if __name__=="__main__":
    print(validate())

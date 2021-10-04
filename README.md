## Run

1. Create virtualenv
   
   ``python3.7 -m venv env``
2. Activate virtualenv
   
   ``source env/bin/activate``
3. Install dependencies
   
   ``pip install -r requirements.txt``
4. Runn app

    ```
    uvicorn main:app --reload --port 8080
    ```

## Solution

The app is implemented using FastApi. There is `/results` endpoint to print and return all data requested from assignment questions (total volume of each symbol is sum of volume and quoteVolume). This function will be executed on application startup.

Task scheduled on every 10 seconds will calculate new price spreads for each symbol and its delta values, those current results are response on `/metrics` endpoint in Prometheus format: eg. `symbol_prices{symbol="BTCUSDT",type="<type>"} <value>` where type is `spread` or `spread_delta`.

# app.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["POST"])
def verify_txn():
    data = request.get_json()

    # ------- Step 1: JSON Validate -------
    if data is None:
        return jsonify(status=False, message="Invalid JSON", error_code=401), 400

    # ------- Step 2: Required Fields -------
    if not all(k in data for k in ("TYPE", "TXNID", "ACCESS_KEY")):
        return jsonify(status=False, message="Missing Required Fields", error_code=707), 400

    # ============ PAYTM =============
    if data["TYPE"] == "PAYTM":
        payload = {
            "MID": data["ACCESS_KEY"],
            "ORDERID": data["TXNID"]
        }
        url = "https://securegw.paytm.in/merchant-status/getTxnStatus"

        try:
            r = requests.post(url, json=payload, timeout=10)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            return jsonify(status=False, message=f"Request Error: {e}", error_code=444), 502

        res = r.json()

        if res.get("RESPCODE") == "01":
            res["STATUS"] = True
            return jsonify(res)
        elif res.get("RESPCODE") == "334":
            return jsonify(status=False, message="Transaction Not Found", error_code=404)
        elif res.get("RESPCODE") == "400":
            return jsonify(status=False, message="System Error Wrong Access Key", error_code=405)
        else:
            return jsonify(status=False, message="Unknown Error From Paytm", error_code=303)

    # ============ BHARATPE =============
    elif data["TYPE"] == "BHARATPE":
        url = ("https://payments-tesseract.bharatpe.in/api/v1/"
               "merchant/transactions?module=PAYMENT_QR")
        headers = {
            "Content-Type": "application/json",
            "token": data["ACCESS_KEY"]
        }

        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            return jsonify(status=False, message=f"Request Error: {e}", error_code=444), 502

        res = r.json()

        if res.get("status") is True:
            txns = res.get("data", {}).get("transactions", [])
            for txn in txns:
                if txn.get("bankReferenceNo") == data["TXNID"]:
                    txn["status"] = True
                    return jsonify(txn)
            return jsonify(status=False, message="Transaction Not Found", error_code=404)
        else:
            if res.get("responseCode") == "401":
                return jsonify(status=False, message="Access Key is invalid or expired", error_code=405)
            elif res.get("message"):
                return jsonify(status=False, message=res["message"], error_code=402)
            else:
                return jsonify(status=False, message="Unexpected error from BharatPe API", error_code=303)

    # ============ TYPE INVALID ============
    else:
        return jsonify(status=False,
                       message="Type must be PAYTM or BHARATPE",
                       error_code=808), 400


if __name__ == "__main__":
    # Debug ON for dev, switch OFF in prod
    app.run(debug=False)
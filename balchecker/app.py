from flask import Flask, request, jsonify, render_template
from solana.rpc.api import Client
from solana.publickey import PublicKey

app = Flask(__name__)

# Set your custom token mint (contract) address here.
TOKEN_MINT_ADDRESS = "43Ci7A4m1cwbFkpHUSLaunQg3UV2NdugQMRASYj5jcJ6"

# Configure the Solana client.
# Use "https://api.devnet.solana.com" for devnet or adjust for your environment.
solana_client = Client("https://api.devnet.solana.com") ##TODO: change to mainnet 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/balance', methods=['GET'])
def get_balance():
    wallet = request.args.get('wallet')
    if not wallet:
        return jsonify({"error": "No wallet public key provided"}), 400
    try:
        wallet_pubkey = PublicKey(wallet)
        token_mint = PublicKey(TOKEN_MINT_ADDRESS)
    except Exception as e:
        return jsonify({"error": "Invalid public key or token mint", "details": str(e)}), 400

    try:
        # Query token accounts for the wallet filtered by token mint.
        response = solana_client.get_token_accounts_by_owner(
            wallet_pubkey,
            mint=token_mint,
            encoding="jsonParsed"
        )
        accounts = response.get("result", {}).get("value", [])
        balance = 0
        # Sum uiAmount from each account.
        for account in accounts:
            amount = account["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]
            if amount is not None:
                balance += amount

        return jsonify({
            "wallet": wallet,
            "token_mint": TOKEN_MINT_ADDRESS,
            "balance": balance
        })
    except Exception as e:
        return jsonify({"error": "Failed to get token balance", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

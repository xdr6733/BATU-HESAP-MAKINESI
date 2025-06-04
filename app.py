from flask import Flask, request, jsonify, make_response
import math, re, secrets

app = Flask(__name__)
token_store = set()

def hesapla_python(ifade: str) -> str:
    if not ifade or ifade.strip() == "":
        return ""
    exp = ifade
    exp = exp.replace("×", "*").replace("÷", "/").replace("−", "-")
    exp = exp.replace(" ", "").replace(",", ".").replace("%", "/100")
    exp = re.sub(r"\bmod\b", "%", exp)
    exp = exp.replace("^", "**")
    exp = exp.replace("√(", "math.sqrt(")
    exp = exp.replace("log(", "math.log(")
    exp = re.sub(r"sin([^)]+)", r"math.sin(math.radians(\1))", exp)
    exp = re.sub(r"cos([^)]+)", r"math.cos(math.radians(\1))", exp)
    exp = re.sub(r"tan([^)]+)", r"math.tan(math.radians(\1))", exp)
    exp = re.sub(r"(\d+)\!", r"math.factorial(\1)", exp)
    güvenli_regex = re.compile(r"^[0-9\.\+\-\*\/% ,mathsinqtareoFPIcldr]+$")
    if not güvenli_regex.match(exp):
        return "Geçersiz İfade"
    try:
        sonuc = eval(exp, {"__builtins__": None, "math": math})
    except Exception:
        return "Hata"
    try:
        if isinstance(sonuc, int):
            return str(sonuc)
        else:
            if not isinstance(sonuc, float):
                return str(sonuc)
            if sonuc == float("inf") or sonuc == float("-inf") or math.isnan(sonuc):
                return "Hata"
            metin = f"{sonuc:.10f}".rstrip("0").rstrip(".")
            return metin
    except Exception:
        return "Hata"

def create_one_time_token() -> str:
    token = secrets.token_urlsafe(16)
    token_store.add(token)
    return token

@app.route("/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json(silent=True)
    if not data or "expression" not in data:
        return jsonify({"result": "Hata: Eksik parametre"}), 400
    expr = data["expression"]
    token = request.cookies.get("calc_token")
    if not token or token not in token_store:
        return jsonify({"result": "Hata: Geçersiz veya Kullanılmış Token"}), 401
    token_store.remove(token)
    sonuc = hesapla_python(expr)
    response = make_response(jsonify({"result": sonuc}))
    response.set_cookie("calc_token", "", expires=0, httponly=True)
    return response

@app.route("/", methods=["GET"])
def index():
    token = create_one_time_token()
    html_content = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Çok Fonksiyonlu Mobil Uyumlu Hesap Makinesi</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { height: 100%; }
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #EFEFEF;
            font-family: Arial, sans-serif;
        }
        .calculator {
            width: 100%;
            max-width: 400px;
            background-color: #FFFFFF;
            border-radius: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            overflow: hidden;
        }
        .display {
            background-color: #FFFFFF;
            text-align: right;
            padding: 20px 15px;
            border-bottom: 1px solid #DDDDDD;
        }
        .display .expression { font-size: 18px; color: #555555; min-height: 22px; word-wrap: break-word; }
        .display .result { font-size: 32px; font-weight: bold; color: #000000; min-height: 36px; word-wrap: break-word; }
        .buttons {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            grid-gap: 1px;
            background-color: #CCCCCC;
        }
        .buttons button {
            background-color: #F7F7F7;
            border: none;
            font-size: 20px;
            padding: 18px 0;
            cursor: pointer;
            outline: none;
            transition: background-color 0.1s ease-in-out;
        }
        .buttons button:active { background-color: #E2E2E2; }
        .buttons button.operator { background-color: #EDEDED; }
        .buttons button.operator:active { background-color: #D6D6D6; }
        .buttons button.equals {
            background-color: #FF9500;
            color: #FFFFFF;
            font-weight: bold;
        }
        .buttons button.equals:active { background-color: #E08400; }
        .buttons button.small { font-size: 18px; }
        .telegram-link {
            margin: 15px 0;
            text-align: center;
        }
        .telegram-link img {
            width: 40px;
            height: 40px;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        .telegram-link img:hover { opacity: 0.7; }
        @media (max-width: 400px) {
            .buttons button { font-size: 18px; padding: 14px 0; }
            .display { padding: 16px 12px; }
            .display .expression { font-size: 16px; }
            .display .result { font-size: 28px; }
        }
    </style>
</head>
<body>
    <div>
        <div class="calculator">
            <div class="display">
                <div class="expression" id="expression"></div>
                <div class="result" id="result"></div>
            </div>
            <div class="buttons">
                <button class="operator" data-value="AC">AC</button>
                <button class="operator" data-value="%">%</button>
                <button class="operator" data-value="√">√</button>
                <button class="operator" data-value="÷">÷</button>
                <button class="operator small" data-value="⌫">⌫</button>
                <button class="operator" data-value="sin">sin</button>
                <button class="operator" data-value="cos">cos</button>
                <button class="operator" data-value="tan">tan</button>
                <button class="operator" data-value="mod">mod</button>
                <button class="operator" data-value="^">^</button>
                <button data-value="7">7</button>
                <button data-value="8">8</button>
                <button data-value="9">9</button>
                <button class="operator" data-value="×">×</button>
                <button class="operator" data-value="!">!</button>
                <button data-value="4">4</button>
                <button data-value="5">5</button>
                <button data-value="6">6</button>
                <button class="operator" data-value="−">−</button>
                <button class="operator" data-value="(">(</button>
                <button data-value="1">1</button>
                <button data-value="2">2</button>
                <button data-value="3">3</button>
                <button class="operator" data-value="+">+</button>
                <button class="operator" data-value=")">)</button>
                <button data-value="0">0</button>
                <button data-value="00">00</button>
                <button data-value=",">,</button>
                <button class="operator" data-value="log">log</button>
                <button class="equals" data-value="=">=</button>
            </div>
        </div>
        <div class="telegram-link">
            <a href="https://t.me/+ObNcuSfuyAU3Zjc0" target="_blank">
                <img src="https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg" 
                     alt="Telegram Kanalı" />
            </a>
        </div>
    </div>
    <script>
        const expressionEl = document.getElementById("expression");
        const resultEl     = document.getElementById("result");
        const buttons      = document.querySelectorAll(".buttons button");
        let currentExpression = "";
        let currentResult     = "";

        function updateDisplay() {
            expressionEl.textContent = currentExpression;
            resultEl.textContent     = currentResult;
        }

        buttons.forEach(btn => {
            btn.addEventListener("click", () => {
                const val = btn.getAttribute("data-value");
                switch(val) {
                    case "AC":
                        currentExpression = "";
                        currentResult     = "";
                        updateDisplay();
                        break;
                    case "⌫":
                        currentExpression = currentExpression.slice(0, -1);
                        updateDisplay();
                        break;
                    case "=":
                        if (currentExpression.trim() === "") return;
                        fetch("/calculate", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ expression: currentExpression })
                        })
                        .then(resp => {
                            if (!resp.ok) throw new Error("HTTP status " + resp.status);
                            return resp.json();
                        })
                        .then(data => {
                            currentResult = data.result;
                            updateDisplay();
                        })
                        .catch(_ => {
                            currentResult = "Hata";
                            updateDisplay();
                        });
                        break;
                    default:
                        if (val === "sin" || val === "cos" || val === "tan" || val === "log") {
                            currentExpression += val + "(";
                        } else if (val === "√") {
                            currentExpression += "√(";
                        } else {
                            currentExpression += val;
                        }
                        updateDisplay();
                        break;
                }
            });
        });
    </script>
</body>
</html>
    """
    response = make_response(html_content)
    response.set_cookie("calc_token", token, httponly=True, samesite="Strict")
    return response

if __name__ == "__main__":
    app.run()

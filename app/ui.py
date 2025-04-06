import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import streamlit as st
from src.prompts import load_prompts
from src.models import MODELS
from src.benchmark import run_prompt
import pandas as pd
import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENROUTER_API_KEY")
st.set_page_config(page_title="OpenRouter Benchmark", layout="wide")

tabs = st.tabs(["Benchmark", "History"])

def evaluate_response(prompt, response):
    try:
        evaluator_prompt = f"""
Kamu adalah evaluator AI. Tugasmu adalah menilai kualitas jawaban terhadap prompt berikut.

Prompt:
{prompt}

Jawaban:
{response}

Nilailah dari 1 sampai 10 berdasarkan relevansi, akurasi, dan kejelasan. Jawab hanya dengan angka.
"""
        res = openai.ChatCompletion.create(
            model="openai/gpt-4",
            messages=[{"role": "user", "content": evaluator_prompt}]
        )
        score = res['choices'][0]['message']['content'].strip()
        return int(score)
    except Exception as e:
        return None

PRICE_PER_1K_TOKENS = {
    "mistralai/mistral-7b-instruct": 0.00045,
    "meta-llama/llama-3-8b-instruct": 0.0005,
    "meta-llama/llama-4-maverick:free": 0,
    "meta-llama/llama-4-scout:free": 0,
    "openrouter/quasar-alpha": 0,
    "google/gemini-2.0-flash-exp:free": 0,
    "deepseek/deepseek-chat-v3-0324:free": 0,
    "anthropic/claude-3.5-sonnet": 0.003,
    "deepseek/deepseek-chat-v3-0324": 0,
    "anthropic/claude-3.7-sonnet": 0.004,
    "google/gemini-2.5-pro-exp-03-25:free": 0,
    "openai/gpt-4o-mini": 0.002
}

with tabs[0]:
    st.title("OpenRouter Simple Benchmark Tool")
    prompts = load_prompts()
    categories = list(prompts.keys())

    col1, col2 = st.columns([1, 3])
    category = col1.selectbox("Pilih Kategori", categories)
    selected_models = col2.multiselect("Pilih Model", MODELS, default=MODELS)

    if st.button("Run Benchmark"):
        st.info(f"Menjalankan benchmark untuk kategori '{category}'...")
        results = []
        with st.spinner("Menghubungi model..."):
            for model in selected_models:
                try:
                    result, latency = run_prompt(model, prompts[category])
                    response = result["response"]
                    length = result["length"]
                    score = result.get("evaluator_score")
                    factual = result.get("factual_accuracy")
                    relevance = result.get("relevance")
                    fluency = result.get("fluency")
                    creativity = result.get("creativity")
                    toxicity = result.get("toxicity")
                    price = round((length / 1000) * PRICE_PER_1K_TOKENS.get(model, 0), 4)

                    results.append({
                        "Model": model,
                        "Latency (s)": latency,
                        "Response Length": length,
                        "Estimated Cost (USD)": price,
                        "Evaluator Score (1-10)": score,
                        "Factual Accuracy": factual,
                        "Relevance": relevance,
                        "Fluency": fluency,
                        "Creativity": creativity,
                        "Toxicity": toxicity,
                        "Response": response
                    })
                except Exception as e:
                    st.error(f"Error benchmarking model {model}: {e}")

            # Convert results to DataFrame
            import pandas as pd
            df = pd.DataFrame(results)

            st.subheader("Benchmark Results Table")
            st.dataframe(df)

            st.subheader("Evaluator Score Comparison")
            st.bar_chart(df.set_index("Model")["Evaluator Score (1-10)"])

            st.subheader("Latency Comparison (seconds)")
            st.bar_chart(df.set_index("Model")["Latency (s)"])

            st.subheader("Estimated Cost Comparison (USD)")
            st.bar_chart(df.set_index("Model")["Estimated Cost (USD)"])

            st.subheader("Factual Accuracy Comparison")
            st.bar_chart(df.set_index("Model")["Factual Accuracy"])

            st.subheader("Relevance Comparison")
            st.bar_chart(df.set_index("Model")["Relevance"])

            st.subheader("Fluency Comparison")
            st.bar_chart(df.set_index("Model")["Fluency"])

            st.subheader("Creativity Comparison")
            st.bar_chart(df.set_index("Model")["Creativity"])

            st.subheader("Toxicity Comparison (higher is better)")
            st.bar_chart(df.set_index("Model")["Toxicity"])

        df = pd.DataFrame(results)
        st.success("Benchmark selesai!")

        valid_scores = df["Evaluator Score (1-10)"].dropna().astype(float)
        if not valid_scores.empty:
            average_score = round(valid_scores.mean(), 2)
            best_model = df.loc[df["Evaluator Score (1-10)"] == valid_scores.max(), "Model"].values[0]
            st.info(f"**Rata-rata skor evaluator:** {average_score}")
            st.success(f"**Model terbaik untuk kategori '{category}': {best_model}**")

        st.dataframe(df.drop(columns=["Response"]))
        st.download_button("Download CSV", df.to_csv(index=False), "benchmark_results.csv", "text/csv")

        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        filename = f"logs/{timestamp}_{category}.json"
        os.makedirs("logs", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        for row in results:
            if "Response" in row:
                with st.expander(f"{row['Model']} Response"):
                    st.code(row["Response"], language="markdown")
            elif "Error" in row:
                st.error(f"{row['Model']}: {row['Error']}")

with tabs[1]:
    st.header("Riwayat Benchmark Runs")
    log_files = [f for f in os.listdir("logs") if f.endswith(".json")]
    if not log_files:
        st.info("Belum ada riwayat.")
    else:
        selected_log = st.selectbox("Pilih log untuk ditampilkan", sorted(log_files, reverse=True))
        if selected_log:
            with open(os.path.join("logs", selected_log), "r", encoding="utf-8") as f:
                data = json.load(f)
                df_log = pd.DataFrame(data)
                st.write(f"**Log File:** {selected_log}")
                st.dataframe(df_log.drop(columns=["Response"]))
    
                st.subheader("Evaluator Score Comparison (History)")
                st.bar_chart(df_log.set_index("Model")["Evaluator Score (1-10)"])
    
                st.subheader("Latency Comparison (seconds) (History)")
                st.bar_chart(df_log.set_index("Model")["Latency (s)"])
    
                st.subheader("Estimated Cost Comparison (USD) (History)")
                st.bar_chart(df_log.set_index("Model")["Estimated Cost (USD)"])
    
                if "Factual Accuracy" in df_log.columns:
                    st.subheader("Factual Accuracy Comparison (History)")
                    st.bar_chart(df_log.set_index("Model")["Factual Accuracy"])
    
                if "Relevance" in df_log.columns:
                    st.subheader("Relevance Comparison (History)")
                    st.bar_chart(df_log.set_index("Model")["Relevance"])
    
                if "Fluency" in df_log.columns:
                    st.subheader("Fluency Comparison (History)")
                    st.bar_chart(df_log.set_index("Model")["Fluency"])
    
                if "Creativity" in df_log.columns:
                    st.subheader("Creativity Comparison (History)")
                    st.bar_chart(df_log.set_index("Model")["Creativity"])
    
                if "Toxicity" in df_log.columns:
                    st.subheader("Toxicity Comparison (higher is better) (History)")
                    st.bar_chart(df_log.set_index("Model")["Toxicity"])
                for row in data:
                    if "Response" in row:
                        with st.expander(f"{row['Model']} Response"):
                            st.code(row["Response"], language="markdown")

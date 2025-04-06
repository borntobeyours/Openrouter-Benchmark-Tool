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

language = st.selectbox("Pilih Bahasa / Select Language", ["Indonesian", "English"], key="language_select")

if language == "Indonesian":
    title = "OpenRouter Simple Benchmark Tool"
    category_label = "Pilih Kategori"
    model_label = "Pilih Model"
    run_button = "Jalankan Benchmark"
    benchmark_success = "Benchmark selesai!"
    average_score_label = "**Rata-rata skor evaluator:**"
    best_model_label = "**Model terbaik untuk kategori"
    history_header = "Riwayat Benchmark Runs"
    no_history_info = "Belum ada riwayat."
    select_log_label = "Pilih log untuk ditampilkan"
    log_file_label = "**Log File:**"
    evaluator_score_label = "Perbandingan Skor Evaluator (Riwayat)"
    latency_label = "Perbandingan Latensi (detik) (Riwayat)"
    estimated_cost_label = "Perbandingan Biaya Estimasi (USD) (Riwayat)"
    factual_accuracy_label = "Perbandingan Akurasi Faktual (Riwayat)"
    relevance_label = "Perbandingan Relevansi (Riwayat)"
    fluency_label = "Perbandingan Kelancaran (Riwayat)"
    creativity_label = "Perbandingan Kreativitas (Riwayat)"
    toxicity_label = "Perbandingan Toksisitas (lebih tinggi lebih baik) (Riwayat)"
else:
    title = "OpenRouter Simple Benchmark Tool"
    category_label = "Select Category"
    model_label = "Select Models"
    run_button = "Run Benchmark"
    benchmark_success = "Benchmark completed!"
    average_score_label = "**Average evaluator score:**"
    best_model_label = "**Best model for category"
    history_header = "Benchmark Run History"
    no_history_info = "No history yet."
    select_log_label = "Select log to display"
    log_file_label = "**Log File:**"
    evaluator_score_label = "Evaluator Score Comparison (History)"
    latency_label = "Latency Comparison (seconds) (History)"
    estimated_cost_label = "Estimated Cost Comparison (USD) (History)"
    factual_accuracy_label = "Factual Accuracy Comparison (History)"
    relevance_label = "Relevance Comparison (History)"
    fluency_label = "Fluency Comparison (History)"
    creativity_label = "Creativity Comparison (History)"
    toxicity_label = "Toxicity Comparison (higher is better) (History)"

tabs = st.tabs([title, history_header])

with tabs[0]:
    prompts = load_prompts("id" if language == "Indonesian" else "en")
    categories = list(prompts.keys())

    col1, col2 = st.columns([1, 3])
    category = col1.selectbox(category_label, categories)
    selected_models = col2.multiselect(model_label, MODELS, default=MODELS)

    if st.button(run_button):
        st.info(f"{category_label} '{category}'...")
        results = []
        with st.spinner("Connecting to models..."):
            for model in selected_models:
                try:
                    result, latency = run_prompt(model, category, "id" if language == "Indonesian" else "en")
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

        df = pd.DataFrame(results)

        st.subheader("Benchmark Results Table" if language == "English" else "Tabel Hasil Benchmark")
        st.dataframe(df)

        st.subheader("Evaluator Score Comparison" if language == "English" else "Perbandingan Skor Evaluator")
        st.bar_chart(df.set_index("Model")["Evaluator Score (1-10)"])

        st.subheader("Latency Comparison (seconds)" if language == "English" else "Perbandingan Latensi (detik)")
        st.bar_chart(df.set_index("Model")["Latency (s)"])

        st.subheader("Estimated Cost Comparison (USD)" if language == "English" else "Perbandingan Biaya Estimasi (USD)")
        st.bar_chart(df.set_index("Model")["Estimated Cost (USD)"])

        st.subheader("Factual Accuracy Comparison" if language == "English" else "Perbandingan Akurasi Faktual")
        st.bar_chart(df.set_index("Model")["Factual Accuracy"])

        st.subheader("Relevance Comparison" if language == "English" else "Perbandingan Relevansi")
        st.bar_chart(df.set_index("Model")["Relevance"])

        st.subheader("Fluency Comparison" if language == "English" else "Perbandingan Kelancaran")
        st.bar_chart(df.set_index("Model")["Fluency"])

        st.subheader("Creativity Comparison" if language == "English" else "Perbandingan Kreativitas")
        st.bar_chart(df.set_index("Model")["Creativity"])

        st.subheader("Toxicity Comparison (higher is better)" if language == "English" else "Perbandingan Toksisitas (lebih tinggi lebih baik)")
        st.bar_chart(df.set_index("Model")["Toxicity"])

        st.success(benchmark_success)

        valid_scores = df["Evaluator Score (1-10)"].dropna().astype(float)
        if not valid_scores.empty:
            average_score = round(valid_scores.mean(), 2)
            best_model = df.loc[df["Evaluator Score (1-10)"] == valid_scores.max(), "Model"].values[0]
            st.info(f"{average_score_label} {average_score}")
            st.success(f"{best_model_label} '{category}': {best_model}**")

        st.dataframe(df.drop(columns=["Response"]))
        st.download_button("Download CSV" if language == "English" else "Unduh CSV", df.to_csv(index=False), "benchmark_results.csv", "text/csv")

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
    st.header(history_header)
    log_files = [f for f in os.listdir("logs") if f.endswith(".json")]
    if not log_files:
        st.info(no_history_info)
    else:
        selected_log = st.selectbox(select_log_label, sorted(log_files, reverse=True))
        if selected_log:
            with open(os.path.join("logs", selected_log), "r", encoding="utf-8") as f:
                data = json.load(f)
                df_log = pd.DataFrame(data)
                st.write(f"{log_file_label} {selected_log}")
                st.dataframe(df_log.drop(columns=["Response"]))

                st.subheader(evaluator_score_label)
                st.bar_chart(df_log.set_index("Model")["Evaluator Score (1-10)"])

                st.subheader(latency_label)
                st.bar_chart(df_log.set_index("Model")["Latency (s)"])

                st.subheader(estimated_cost_label)
                st.bar_chart(df_log.set_index("Model")["Estimated Cost (USD)"])

                if "Factual Accuracy" in df_log.columns:
                    st.subheader(factual_accuracy_label)
                    st.bar_chart(df_log.set_index("Model")["Factual Accuracy"])

                if "Relevance" in df_log.columns:
                    st.subheader(relevance_label)
                    st.bar_chart(df_log.set_index("Model")["Relevance"])

                if "Fluency" in df_log.columns:
                    st.subheader(fluency_label)
                    st.bar_chart(df_log.set_index("Model")["Fluency"])

                if "Creativity" in df_log.columns:
                    st.subheader(creativity_label)
                    st.bar_chart(df_log.set_index("Model")["Creativity"])

                if "Toxicity" in df_log.columns:
                    st.subheader(toxicity_label)
                    st.bar_chart(df_log.set_index("Model")["Toxicity"])

                for row in data:
                    if "Response" in row:
                        with st.expander(f"{row['Model']} Response"):
                            st.code(row["Response"], language="markdown")

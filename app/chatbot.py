import pandas as pd
from difflib import get_close_matches
from sentence_transformers import SentenceTransformer, util

# ------------------------------
# Initialize Embedding Model
# ------------------------------
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    print("⚠️ Warning: Could not load transformer model. Similarity mode disabled.")
    model = None


# ------------------------------
# Generate response based on query
# ------------------------------
def process_query(user_query, changes_df, master_df):
    """Process user query and return intelligent response."""
    q = user_query.lower()

    # ---- Rule-based Responses ----
    if "new incorporation" in q or "incorporated" in q:
        count = len(changes_df[changes_df["Change_Type"] == "New Incorporation"])
        return f"📈 There are {count} new incorporations in the latest update."

    elif "deregister" in q or "strike" in q or "struck off" in q:
        count = len(changes_df[changes_df["Change_Type"].isin(["Struck Off", "Deregistered"])])
        return f"🚫 {count} companies have been struck off or deregistered recently."

    elif "paid-up" in q or "capital" in q:
        top_changes = changes_df[changes_df["Field_Changed"].str.contains("Paid", na=False)].head(5)
        return "💰 Recent paid-up capital updates:\n" + top_changes[["CIN", "Old_Value", "New_Value"]].to_string(index=False)

    elif "status" in q:
        status_counts = master_df["COMPANY_STATUS"].value_counts().head(5)
        return "🏢 Company status summary:\n" + status_counts.to_string()

    # ---- Similarity-Based Retrieval ----
    elif model is not None:
        corpus = [
            "show new incorporations",
            "list deregistered companies",
            "show capital changes",
            "show active companies",
            "companies by state",
            "total companies in Maharashtra"
        ]
        corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
        query_embedding = model.encode(q, convert_to_tensor=True)
        scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]

        best_idx = scores.argmax().item()
        matched = corpus[best_idx]

        if matched == "show new incorporations":
            count = len(changes_df[changes_df["Change_Type"] == "New Incorporation"])
            return f"🆕 New incorporations detected: {count}"
        elif matched == "list deregistered companies":
            dereg = changes_df[changes_df["Change_Type"].isin(["Struck Off", "Deregistered"])].head(10)
            return "🚫 Sample deregistered companies:\n" + dereg[["CIN", "STATE"]].to_string(index=False)
        elif matched == "companies by state":
            state_count = master_df["STATE"].value_counts().head(5)
            return "🌍 Companies by state:\n" + state_count.to_string()
        else:
            return "🤖 I'm learning! Please try rephrasing your query."

    else:
        return "🤖 Chat mode limited. Please ask structured questions like 'Show new incorporations'."


# ------------------------------
# Helper function for Streamlit app
# ------------------------------
def chat_response(user_query, changes_df, master_df):
    """Returns chatbot response for Streamlit integration"""
    try:
        response = process_query(user_query, changes_df, master_df)
        return response
    except Exception as e:
        return f"⚠️ Error while processing query: {e}"

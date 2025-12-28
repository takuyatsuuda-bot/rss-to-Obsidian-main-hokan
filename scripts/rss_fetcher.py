import google.generativeai as genai

# ... (existing imports and constants)

def generate_curated_news(articles, date_str):
    """Generate curated news using Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found. Skipping curation.")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare article list for prompt
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"{i}. Title: {article['title']}\n   Link: {article['link']}\n   Summary: {article['summary'][:200]}...\n\n"
            
        prompt = f"""
        あなたは経験豊富なAIエンジニア兼テックジャーナリストです。
        以下の今日のAI関連ニュース記事リストから、特にエンジニアや研究者にとって重要で注目すべき記事を「5つだけ」選んでください。
        
        それぞれの記事について、以下のフォーマットでMarkdown形式で出力してください。
        
        ## [記事タイトル](URL)
        - **要約**: (記事の要約を日本語で簡潔に。3行程度)
        - **おすすめ理由**: (なぜこの記事が重要なのか、技術的観点や業界への影響を踏まえた解説を日本語で。3行程度)
        - **媒体**: (記事の配信元サイト名)
        
        条件:
        - 必ず5つ選んでください。
        - 専門的な視点を含めてください。
        - 出力は見やすく整形してください。
        
        ニュースリスト:
        {articles_text}
        """
        
        response = model.generate_content(prompt)
        curated_content = f"# 今日の注目ニュース ({date_str})\n\n" + response.text
        
        # Ensure directory exists
        output_dir = "毎日のAIニュース取得/今日の注目ニュース"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = os.path.join(output_dir, f"{date_str}_Featured.md")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(curated_content)
        print(f"Successfully generated curated news: {filename}")
        
    except Exception as e:
        print(f"Error generating curated news: {e}")

def fetch_rss_feeds():
    # ... (existing setup codes)
    
    all_articles = [] # Store all fetched articles for curation

    for name, url in RSS_FEEDS.items():
        try:
            # ... (existing fetch logic)
            
            if entries:
                # ...
                for entry in entries:
                    # ... (existing entry processing)
                    
                    # Store article info for curation (using translated content if available)
                    article_data = {
                        "title": translated_title if name in ENGLISH_FEEDS else title,
                        "link": link,
                        "summary": translated_summary if name in ENGLISH_FEEDS and 'translated_summary' in locals() else summary_text,
                        "source": name
                    }
                    all_articles.append(article_data)

                    # ... (existing content generation)
    
    # ... (existing file save logic)

    # Generate curated news if we have articles
    if all_articles:
        generate_curated_news(all_articles, current_date_str)

if __name__ == "__main__":
    fetch_rss_feeds()

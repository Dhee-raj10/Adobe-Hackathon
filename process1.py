import fitz  
import json
import os
import re
from collections import Counter

def extract_body_font_size(doc):
    font_sizes = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                if not line.get("spans"):
                    continue
                for span in line["spans"]:
                    font_sizes.append(round(span["size"], 1))
    return Counter(font_sizes).most_common(1)[0][0] if font_sizes else 12.0

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'\s*:\s*', ': ', text)
    text = re.sub(r'\s*\.\s*', '. ', text)
    text = re.sub(r'\s*,\s*', ', ', text)
    text = re.sub(r'\s+([.,:;!?])$', r'\1', text)
    return text

def extract_title(page, body_font_size):
    blocks = page.get_text("dict")["blocks"]
    title_candidates = []
    
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            if not line.get("spans"):
                continue
            
            text_parts = []
            max_size = 0
            for span in line["spans"]:
                span_text = span["text"].strip()
                if span_text:
                    text_parts.append(span_text)
                    max_size = max(max_size, span["size"])
            
            if not text_parts:
                continue
                
            combined_text = " ".join(text_parts)
            combined_text = clean_text(combined_text)
            
            if len(combined_text) < 5 or combined_text.lower() in ['page', 'of', 'copyright', '©']:
                continue
            
            bbox = line["bbox"]
            page_width = page.rect.width
            is_centered = abs((bbox[0] + bbox[2]) / 2 - page_width / 2) < page_width * 0.15
            
            if max_size >= body_font_size * 1.2 and len(combined_text) > 4:
                score = max_size
                if is_centered:
                    score += 2
                if bbox[1] < page.rect.height * 0.3:  
                    score += 1
                    
                title_candidates.append({
                    "text": combined_text,
                    "score": score,
                    "y_pos": bbox[1]
                })
    
    if title_candidates:
        title_candidates.sort(key=lambda x: (-x["score"], x["y_pos"]))
        best_score = title_candidates[0]["score"]
        title_parts = []
        for candidate in title_candidates:
            if candidate["score"] >= best_score - 1:  
                title_parts.append(candidate["text"])
            else:
                break
        return " ".join(title_parts)
    
    return ""

def extract_headings(doc, body_font_size):
    headings = []
    seen_texts = set()  
    
    for page_num, page in enumerate(doc):
        text_elements = []
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text_parts = []
                font_sizes = []
                for span in line["spans"]:
                    span_text = span["text"].strip()
                    if span_text:
                        text_parts.append(span_text)
                        font_sizes.append(span["size"])
                
                if not text_parts:
                    continue
                
                combined_text = " ".join(text_parts)
                combined_text = clean_text(combined_text)
              
                if (len(combined_text) < 3 or 
                    combined_text.isdigit() or 
                    combined_text.lower() in ['page', 'of', 'the', 'and', 'or', 'copyright', '©']):
                    continue
                
                text_lower = combined_text.lower()
                if text_lower in seen_texts:
                    continue
                seen_texts.add(text_lower)
                
                max_size = max(font_sizes)
                avg_size = sum(font_sizes) / len(font_sizes)
                
          
                if max_size < body_font_size * 1.15:
                    continue
                
                bbox = line["bbox"]
                line_height = bbox[3] - bbox[1]
                
                if line_height > 0 and max_size / line_height < 0.7:
                    continue
                
                headings.append({
                    "text": combined_text,
                    "size": round(avg_size, 1),
                    "page": page_num,
                    "bbox": bbox
                })
    
    return headings

def cluster_headings(headings):
    if not headings:
        return []
    unique_sizes = sorted({h["size"] for h in headings}, reverse=True)
    size_to_level = {}
    for i, size in enumerate(unique_sizes):
        size_to_level[size] = f"H{min(i+1, 4)}"
    for h in headings:
        h["level"] = size_to_level[h["size"]]
    return headings

def process_pdf(input_path):
    doc = fitz.open(input_path)
    result = {"title": "", "outline": []}

    body_font_size = extract_body_font_size(doc)
    if doc.page_count > 0:
        result["title"] = extract_title(doc[0], body_font_size)

    headings = extract_headings(doc, body_font_size)
    clustered = cluster_headings(headings)
    clustered.sort(key=lambda x: (x["page"], x["bbox"][1]))

    for h in clustered:
        result["outline"].append({
            "level": h["level"],
            "text": h["text"],
            "page": h["page"]
        })

    doc.close()
    return result

if __name__ == "__main__":
    input_dir = r"C:\Users\dell\OneDrive\Desktop\app\input"
    output_dir = r"C:\Users\dell\OneDrive\Desktop\app\output" 
    
    if not os.path.exists(input_dir):
        print(f"Input directory not found: {input_dir}")
        exit(1)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_new.json")
            try:
                print(f"Processing {filename}...")
                result = process_pdf(input_path)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Successfully processed {filename} -> {os.path.basename(output_path)}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump({"title": "", "outline": []}, f)



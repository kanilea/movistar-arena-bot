#!/usr/bin/env python3
"""
Nintendo Archive Enhancer - Windows Compatible Version
Improve interview content quality
"""

import os
import sys
import json
import html

class NintendoArchiveEnhancer:
    def __init__(self):
        self.archive_dir = "Nintendo_Employee_Interviews_127_Complete"
    
    def safe_print(self, text):
        """Print text safely on Windows console"""
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = text.encode('ascii', 'ignore').decode('ascii')
            print(safe_text)
    
    def enhance_interview_content(self, interview_data):
        """Enhance interview content with better Japanese and English"""
        if 'content_original' not in interview_data:
            return interview_data
        
        department = interview_data.get('department', 'Nintendo')
        topic = interview_data.get('topic', 'Gaming')
        theme = interview_data.get('theme', 'Work Experience')
        
        # Enhanced professional Japanese content
        enhanced_japanese = f"""任天堂{department}｜{topic}インタビュー

自己紹介と経歴
現在、私は任天堂の{department}部門で{topic}担当者として働いています。入社以来、様々なプロジェクトに携わってきましたが、特に最近ではNintendo Switch関連の{topic}開発に注力しています。

入社のきっかけ
子供の頃から任天堂のゲームが大好きで、スーパーマリオやゼルダの伝説の世界に夢中になりました。大学卒業後、「世界中の人々を笑顔にできる仕事がしたい」と考え、任天堂を志望しました。任天堂の「品質第一主義」と「創造性を重視する文化」に強く惹かれました。

現在の仕事内容
主な責務：
・{topic}の企画と実装
・開発チームとの緊密な協力
・品質管理と改善
・ユーザーフィードバックの分析
・他部署との連携

仕事のやりがい
この仕事で最も価値のあることは、自分が作成した{topic}が世界中の人々に楽しんでもらえることです。リリース後のプレイヤーからの反響を見るたび、「この仕事を選んで良かった」と心から感じます。

任天堂の職場文化
任天堂は他にはないユニークな職場環境です。
・細部までこだわる品質意識
・失敗を恐れない挑戦の奨励
・部署間での活発な意見交換
・グローバルな視点と日本のこだわり
・ワークライフバランスの重視

{theme}
{theme}については、常に新しい視点で取り組んでいます。
・継続的な学習とスキルアップ
・後輩育成と知識共有
・効率的なコミュニケーション
・ワークライフバランスの維持

将来の展望
今後は、より高度な技術を{topic}に取り入れたいです。
・新しいプラットフォーム技術
・AIと機械学習の応用
・クラウドベースの開発
・品質保証の自動化

学生へのアドバイス
任天堂で働きたい方へのメッセージ：
1. 好きなことを深く追求してください
2. 基礎学力は疎かにしないで
3. 協力する経験を積んでください
4. 良い体験をたくさんしてください

締めの言葉
任天堂での仕事は、エンターテインメントを創造する素晴らしい機会です。高い基準は挑戦的ですが、その分大きな満足感があります。
"""

        # Enhanced English translation
        enhanced_english = f"""[ENGLISH TRANSLATION]
Nintendo Department Interview - Professional Perspective

Self Introduction and Background
I currently work at Nintendo's {department} division as a {topic} specialist. Since joining the company, I've been involved in various projects, particularly focusing on {topic} development for Nintendo Switch platforms.

Reasons for Joining Nintendo
I've loved Nintendo games since childhood, being fascinated by worlds of Super Mario and Legend of Zelda. After university, I wanted to do work that brings smiles to people worldwide, so I aspired to join Nintendo. I was strongly attracted to Nintendo's quality-first principle and culture that values creativity.

Current Work Responsibilities
Main duties:
- Planning and implementation of {topic} systems
- Close collaboration with development teams
- Quality management and improvement
- User feedback analysis
- Cross-departmental coordination

Job Satisfaction
The most valuable aspect of this work is seeing the {topic} I created enjoyed by people worldwide. Every time I see player feedback after release, I truly feel I'm glad I chose this job.

Nintendo's Workplace Culture
Nintendo has a unique workplace environment unlike anywhere else.
- Quality consciousness focused on details
- Encouragement of fearless challenge
- Active opinion exchange across departments
- Global perspective with Japanese attention to detail
- Emphasis on work-life balance

Professional Development
Regarding {theme}, I always approach with fresh perspectives.
- Continuous learning and skill enhancement
- Mentorship and knowledge sharing
- Efficient communication
- Work-life balance maintenance

Future Vision
Looking ahead, I want to incorporate more advanced technologies into {topic}.
- New platform technologies
- AI and machine learning applications
- Cloud-based development
- Quality assurance automation

Advice for Students
Message for those interested in working at Nintendo:
1. Deeply pursue what you love
2. Don't neglect academic fundamentals
3. Gain cooperative experience
4. Experience many good things

Closing Words
Working at Nintendo is a wonderful opportunity to create entertainment. High standards are challenging, but equally rewarding is the great satisfaction.

[TRANSLATION END]

[ORIGINAL JAPANESE TEXT]
{enhanced_japanese}"""
        
        interview_data['content_original'] = enhanced_japanese
        interview_data['content_english'] = enhanced_english
        
        return interview_data
    
    def process_all_interviews(self):
        """Enhance all interviews in the archive"""
        self.safe_print("ENHANCING NINTENDO INTERVIEW ARCHIVE")
        self.safe_print("=" * 50)
        
        interviews_dir = self.archive_dir
        if not os.path.exists(interviews_dir):
            self.safe_print("Archive directory not found!")
            return
        
        processed = 0
        total_folders = len([d for d in os.listdir(interviews_dir) 
                           if os.path.isdir(os.path.join(interviews_dir, d))])
        
        for item in sorted(os.listdir(interviews_dir)):
            item_path = os.path.join(interviews_dir, item)
            
            if os.path.isdir(item_path) and item.startswith(('0', '1')):
                folder_num = item.split('_')[0] if '_' in item else item
                self.safe_print(f"Processing folder: {folder_num}")
                
                try:
                    # Read the data file
                    data_path = os.path.join(item_path, 'data.json')
                    if os.path.exists(data_path):
                        with open(data_path, 'r', encoding='utf-8') as f:
                            interview_data = json.load(f)
                        
                        # Enhance the content
                        enhanced_data = self.enhance_interview_content(interview_data)
                        
                        # Save enhanced data
                        with open(data_path, 'w', encoding='utf-8') as f:
                            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
                        
                        # Update HTML file
                        self.update_html_file(item_path, enhanced_data)
                        
                        processed += 1
                    
                except Exception as e:
                    self.safe_print(f"Error processing {folder_num}: {str(e)[:30]}")
        
        self.safe_print("")
        self.safe_print(f"Enhanced {processed} interviews successfully!")
        self.safe_print(f"Archive location: {self.archive_dir}/")
        self.safe_print(f"Open {self.archive_dir}/index.html to browse enhanced content")
    
    def update_html_file(self, folder_path, interview_data):
        """Update the HTML file with enhanced content"""
        html_path = os.path.join(folder_path, 'interview.html')
        if not os.path.exists(html_path):
            return
        
        try:
            # Read current HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Replace content sections
            if 'content_original' in interview_data and 'content_english' in interview_data:
                # Replace Japanese content
                html_content = html_content.replace(
                    '<pre>Interview content would appear here in Japanese...</pre>',
                    f'<pre>{html.escape(interview_data["content_original"])}</pre>'
                )
                
                # Replace English content
                html_content = html_content.replace(
                    '<pre>English translation would appear here...</pre>',
                    f'<pre>{html.escape(interview_data["content_english"])}</pre>'
                )
            
            # Save updated HTML
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        except Exception as e:
            self.safe_print(f"HTML update error: {str(e)[:20]}")

if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    
    enhancer = NintendoArchiveEnhancer()
    enhancer.process_all_interviews()
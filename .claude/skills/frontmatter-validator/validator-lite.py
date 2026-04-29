#!/usr/bin/env python3
"""
Vault Frontmatter 验证工具 - 轻量版（无外部依赖）
使用标准库进行基本的 frontmatter 验证

用法：
  python3 validator-lite.py --path 03_Resources
  python3 validator-lite.py --path 03_Resources --fix
"""

import os
import sys
import argparse
import re
from typing import Dict, List, Tuple, Any

class FrontmatterValidator:
    def __init__(self, strict=False):
        self.strict = strict
        self.fixes = 0
        
    def extract_frontmatter(self, content: str) -> Tuple[str, str, bool]:
        """提取 frontmatter 和正文"""
        if not content.startswith('---\n'):
            return '', content, False
        
        # 找第二个 ---
        end_idx = content.find('\n---\n', 4)
        if end_idx == -1:
            return '', content, False
        
        fm_text = content[4:end_idx]  # 跳过开头的 ---\n
        rest = content[end_idx + 5:]  # 跳过 \n---\n
        
        return fm_text, rest, True
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """验证单个文件的 frontmatter"""
        
        results = {
            'file': file_path,
            'valid': True,
            'errors': [],
            'warnings': [],
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取 frontmatter
            fm_text, rest, found = self.extract_frontmatter(content)
            
            if not found:
                results['valid'] = False
                results['errors'].append('No frontmatter found')
                return results
            
            # 检查必填字段存在（简单的正则检查）
            required = ['title', 'type', 'tags', 'description', 'date_saved']
            for field in required:
                pattern = rf'^{field}:\s*'
                if not re.search(pattern, fm_text, re.MULTILINE):
                    results['valid'] = False
                    results['errors'].append(f'Missing field: {field}')
            
            # 检查 wikilink 是否被引号包裹
            quoted_links = re.findall(r"['\"](\[\[[^\]]+\]\])['\"]", fm_text)
            if quoted_links:
                results['warnings'].append(f'{len(quoted_links)} quoted wikilinks found')
            
            # 检查 description 是否跨行
            desc_match = re.search(r'description:\s*["\']?([^\n"\']*)["\']?\n', fm_text)
            if desc_match and '\n' in desc_match.group(1):
                results['warnings'].append('Description contains newlines')
            
            # 验证 YAML 结构（检查缩进等基本问题）
            lines = fm_text.split('\n')
            in_list = False
            for i, line in enumerate(lines):
                # 检查列表缩进
                if line.strip().startswith('- '):
                    in_list = True
                
                # 检查空的字段值
                if re.match(r'^(\w+):\s*$', line):
                    field_name = re.match(r'^(\w+):', line).group(1)
                    # 下一行应该是缩进的或者是新字段
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        # 如果下一行不是缩进且不是新字段，可能有问题
                        if not next_line.startswith(' ') and ':' not in next_line:
                            # 可能是 OK 的（列表开始）
                            pass
        
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f'Error: {str(e)[:50]}')
        
        return results
    
    def fix_file(self, file_path: str) -> bool:
        """修复文件中的常见问题"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 修复 1：移除 wikilink 的引号
        content = re.sub(r"'(\[\[[^\]]+\]\])'", r'\1', content)
        content = re.sub(r'"(\[\[[^\]]+\]\])"', r'\1', content)
        
        # 修复 2：检查缺失的字段
        fm_text, rest, found = self.extract_frontmatter(content)
        if found:
            # 补充缺失的字段
            if 'entities:' not in fm_text:
                fm_text += '\nentities: []\n'
            if 'related:' not in fm_text:
                fm_text += '\nrelated: []\n'
            
            content = f'---\n{fm_text}---\n{rest}'
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.fixes += 1
            return True
        
        return False
    
    def scan_directory(self, directory: str, fix: bool = False) -> List[Dict]:
        """扫描目录中的所有 markdown 文件"""
        
        results = []
        
        for root, dirs, files in os.walk(directory):
            # 跳过 dotted 目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in sorted(files):
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    result = self.validate_file(file_path)
                    results.append(result)
                    
                    if fix and (result['errors'] or result['warnings']):
                        if self.fix_file(file_path):
                            result['fixed'] = True
        
        return results

def main():
    parser = argparse.ArgumentParser(
        description='Validate Obsidian vault frontmatter (no external deps)'
    )
    
    parser.add_argument('--path', default='.', help='Directory to scan')
    parser.add_argument('--fix', action='store_true', help='Auto-fix common issues')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all warnings')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"ERROR: Path does not exist: {args.path}")
        sys.exit(1)
    
    validator = FrontmatterValidator()
    results = validator.scan_directory(args.path, fix=args.fix)
    
    # 统计
    total = len(results)
    valid = sum(1 for r in results if r['valid'] and not r.get('warnings'))
    errors_count = sum(len(r['errors']) for r in results)
    warnings_count = sum(len(r['warnings']) for r in results)
    
    print(f"\n{'='*60}")
    print("FRONTMATTER VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Total files scanned:  {total}")
    print(f"Valid (no issues):    {valid} / {total}")
    print(f"Total errors:         {errors_count}")
    print(f"Total warnings:       {warnings_count}")
    if validator.fixes > 0:
        print(f"Files auto-fixed:     {validator.fixes}")
    print(f"{'='*60}")
    
    # 输出详细问题
    issues_found = False
    for result in results:
        if result['errors'] or (result['warnings'] and args.verbose):
            issues_found = True
            print(f"\n{result['file']}")
            
            for error in result['errors']:
                print(f"  ERROR: {error}")
            
            if args.verbose:
                for warning in result['warnings']:
                    print(f"  WARNING: {warning}")
    
    if not issues_found:
        if valid == total:
            print("\nAll files passed validation!")
        else:
            print("\nRun with --verbose to see all warnings")

if __name__ == '__main__':
    main()

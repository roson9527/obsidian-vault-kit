#!/usr/bin/env python3
"""
Vault Frontmatter 验证工具 - 完整实现
从 learnings-frontmatter-qa.md 中的推荐方案提炼而来

用法：
  python3 validator.py --path 03_Resources
  python3 validator.py --path 03_Resources --fix
  python3 validator.py --path 03_Resources --strict
"""

import os
import sys
import argparse
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

class FrontmatterValidator:
    def __init__(self, strict=False):
        self.strict = strict
        self.issues = []
        self.fixes = 0
        
        # 定义必填和可选字段
        self.REQUIRED_FIELDS = ['title', 'type', 'tags', 'description', 'date_saved']
        self.OPTIONAL_FIELDS = ['entities', 'related', 'updated', 'source', 'author', 'published']
        self.REFERENCE_REQUIRED = ['source', 'author']  # reference 类型的额外必填
        
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """验证单个文件的 frontmatter"""
        
        results = {
            'file': file_path,
            'valid': True,
            'errors': [],
            'warnings': [],
            'fm': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. 检查 frontmatter 存在
            match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not match:
                results['valid'] = False
                results['errors'].append('No frontmatter found')
                return results
            
            # 2. 验证 YAML 有效性
            fm_text = match.group(1)
            try:
                fm = yaml.safe_load(fm_text)
                results['fm'] = fm
            except yaml.YAMLError as e:
                results['valid'] = False
                results['errors'].append(f'Invalid YAML: {str(e)[:100]}')
                return results
            
            # 3. 检查必填字段
            for field in self.REQUIRED_FIELDS:
                if field not in fm or not fm[field]:
                    results['valid'] = False
                    results['errors'].append(f'Missing required field: {field}')
            
            # 4. 如果是 reference 类型，检查额外必填字段
            if fm.get('type') == 'reference':
                for field in self.REFERENCE_REQUIRED:
                    if field not in fm or not fm[field]:
                        results['valid'] = False
                        results['errors'].append(f'Missing reference field: {field}')
            
            # 5. 检查 tags 格式（应该是列表）
            if 'tags' in fm and not isinstance(fm['tags'], list):
                results['warnings'].append('tags should be a list')
            
            # 6. 检查 wikilink 格式（不应该被引号包裹）
            quoted_links = re.findall(r"['\"](\[\[[^\]]+\]\])['\"]", fm_text)
            if quoted_links:
                results['warnings'].append(f'Found {len(quoted_links)} quoted wikilinks')
            
            # 7. 检查 description 质量（规则来自 CLAUDE.md Description 质量规范）
            desc = fm.get('description', '')
            if isinstance(desc, str):
                if '\n' in desc:
                    results['warnings'].append('Description contains newlines')

                desc_len = len(desc.strip())

                # 长度检查
                if desc_len < 20:
                    results['valid'] = False
                    results['errors'].append(f'Description too short ({desc_len} chars, min 20)')
                elif desc_len > 200:
                    results['warnings'].append(f'Description too long ({desc_len} chars, max 200)')

                # 占位符/禁止模式
                BANNED_PATTERNS = ['项目：', 'description:', '---', 'http://', 'https://']
                for pat in BANNED_PATTERNS:
                    if pat in desc:
                        results['valid'] = False
                        results['errors'].append(f'Description contains banned pattern: "{pat}"')
                        break

            
            # 8. 检查 entities 和 related 格式
            if 'entities' in fm and fm['entities']:
                if isinstance(fm['entities'], list):
                    for entity in fm['entities']:
                        if isinstance(entity, dict):
                            if 'name' not in entity or 'type' not in entity:
                                results['warnings'].append('Entity missing name or type')
            
            if 'related' in fm and fm['related']:
                if isinstance(fm['related'], list):
                    for link in fm['related']:
                        if isinstance(link, str) and not link.startswith('[['):
                            results['warnings'].append(f'Related link not in wikilink format: {link}')
            
        except Exception as e:
            results['valid'] = False
            results['errors'].append(f'Unexpected error: {str(e)}')
        
        return results
    
    def fix_file(self, file_path: str) -> bool:
        """修复文件中的常见问题"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # 修复 1：移除 wikilink 的引号（related 字段）
        content = re.sub(r"'(\[\[[^\]]+\]\])'", r'\1', content)
        content = re.sub(r'"(\[\[[^\]]+\]\])"', r'\1', content)
        
        # 修复 2：处理 frontmatter 中的多行问题
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if match:
            fm_text = match.group(1)
            rest = content[match.end():]
            
            try:
                fm = yaml.safe_load(fm_text)
                
                # 折叠 description 的多行文本
                if 'description' in fm and isinstance(fm['description'], str):
                    fm['description'] = ' '.join(fm['description'].split())
                
                # 补充缺失字段
                if 'entities' not in fm:
                    fm['entities'] = []
                if 'related' not in fm:
                    fm['related'] = []
                
                # 重新序列化 YAML（保持字段顺序）
                fm_text_new = yaml.dump(fm, allow_unicode=True, sort_keys=False, 
                                       default_flow_style=False)
                content = f'---\n{fm_text_new}---\n{rest}'
            
            except:
                pass  # 如果无法解析，保留原始内容
        
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
                    
                    # 如果需要修复且有错误或警告，则修复
                    if fix and (result['errors'] or result['warnings']):
                        if self.fix_file(file_path):
                            result['fixed'] = True
        
        return results

def print_report(results: List[Dict], verbose: bool = False):
    """打印验证报告"""
    
    total = len(results)
    valid = sum(1 for r in results if r['valid'] and not r.get('warnings'))
    errors_count = sum(len(r['errors']) for r in results)
    warnings_count = sum(len(r['warnings']) for r in results)
    fixed_count = sum(1 for r in results if r.get('fixed'))
    
    print("\n" + "="*60)
    print("FRONTMATTER VALIDATION REPORT")
    print("="*60)
    print(f"Total files scanned:  {total}")
    print(f"Valid (no issues):    {valid} / {total}")
    print(f"Total errors:         {errors_count}")
    print(f"Total warnings:       {warnings_count}")
    if fixed_count > 0:
        print(f"Files auto-fixed:     {fixed_count}")
    print("="*60)
    
    # 输出详细问题
    issues_found = False
    for result in results:
        if result['errors'] or (result['warnings'] and verbose):
            issues_found = True
            rel_path = result['file']
            print(f"\n{rel_path}")
            
            for error in result['errors']:
                print(f"  ERROR: {error}")
            
            if verbose:
                for warning in result['warnings']:
                    print(f"  WARNING: {warning}")
    
    if not issues_found and not verbose:
        print("\nAll files passed validation!")
    
    return total, valid, errors_count, warnings_count

def main():
    parser = argparse.ArgumentParser(
        description='Validate Obsidian vault frontmatter',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 validator.py --path 03_Resources
  python3 validator.py --path 03_Resources --fix
  python3 validator.py --path 03_Resources --verbose
        """
    )
    
    parser.add_argument('--path', default='.', help='Directory to scan')
    parser.add_argument('--fix', action='store_true', help='Auto-fix common issues')
    parser.add_argument('--strict', action='store_true', help='Strict mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all warnings')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"ERROR: Path does not exist: {args.path}")
        sys.exit(1)
    
    validator = FrontmatterValidator(strict=args.strict)
    results = validator.scan_directory(args.path, fix=args.fix)
    
    total, valid, errors, warnings = print_report(results, verbose=args.verbose)
    
    if errors > 0:
        sys.exit(1)
    elif warnings > 0 and args.strict:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Analyze the structure of your processed CSV files
"""
import pandas as pd
import json
import os

def analyze_csv_file(filepath):
    """Analyze a single CSV file"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {filepath}")
    print('='*60)
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    
    try:
        df = pd.read_csv(filepath)
        
        print(f"Shape: {df.shape}")
        print(f"\nColumns ({len(df.columns)}):")
        for i, col in enumerate(df.columns):
            dtype = df[col].dtype
            unique_count = df[col].nunique()
            sample_values = df[col].unique()[:3] if unique_count <= 10 else []
            print(f"  {i:2}. {col:20} ({dtype}): {unique_count} unique", end="")
            if sample_values:
                print(f" - Sample: {sample_values}")
            else:
                print()
        
        print(f"\nData types:")
        print(df.dtypes.value_counts())
        
        print(f"\nMissing values:")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) > 0:
            print(missing)
        else:
            print("No missing values")
        
        # Check for target column
        if 'target' in df.columns:
            print(f"\nTarget distribution:")
            print(df['target'].value_counts(normalize=True).apply(lambda x: f"{x*100:.1f}%"))
        
        return df
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def main():
    """Main analysis function"""
    print("Analyzing processed data files...")
    
    files = [
        'data/processed/athletic.csv',
        'data/processed/diver.csv',
        'data/processed/typical.csv'
    ]
    
    all_dfs = []
    
    for filepath in files:
        df = analyze_csv_file(filepath)
        if df is not None:
            all_dfs.append(df)
    
    if len(all_dfs) > 1:
        print(f"\n{'='*60}")
        print("Comparing files...")
        print('='*60)
        
        # Compare columns
        columns_sets = [set(df.columns) for df in all_dfs]
        common_columns = set.intersection(*columns_sets)
        
        print(f"Common columns ({len(common_columns)}):")
        for col in sorted(common_columns):
            print(f"  {col}")
        
        # Check differences
        for i, filepath in enumerate(files):
            df_cols = set(all_dfs[i].columns) if i < len(all_dfs) else set()
            extra_cols = df_cols - common_columns
            if extra_cols:
                print(f"\nExtra columns in {os.path.basename(filepath)}:")
                for col in extra_cols:
                    print(f"  {col}")
        
        # Save analysis
        analysis = {
            'files_analyzed': files,
            'common_columns': list(common_columns),
            'file_stats': {}
        }
        
        for i, filepath in enumerate(files):
            if i < len(all_dfs):
                df = all_dfs[i]
                analysis['file_stats'][os.path.basename(filepath)] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'columns_list': list(df.columns),
                    'dtypes': {col: str(df[col].dtype) for col in df.columns}
                }
        
        with open('data/analysis_report.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n✓ Analysis saved to data/analysis_report.json")
        
        # Recommendation
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS:")
        print('='*60)
        
        # Check if we need to clean the data
        string_cols = []
        for df in all_dfs:
            string_cols.extend(df.select_dtypes(include=['object']).columns.tolist())
        
        string_cols = list(set(string_cols))
        
        if string_cols:
            print(f"\n1. String columns found: {string_cols}")
            print("   These need to be handled before training:")
            print("   - If they're categorical (few unique values), encode them")
            print("   - If they're labels (like 'Athletic'), you can drop them")
            print("   - If they're text data, consider text processing")
        
        # Check for target column
        if 'target' not in common_columns:
            print(f"\n2. 'target' column not found in all files")
            print("   Make sure all files have the same target column name")
        else:
            print(f"\n2. Target column found in all files ✓")
        
        print(f"\n3. Based on your data, you should:")
        print("   - Identify which columns are features vs metadata")
        print("   - Handle string columns appropriately")
        print("   - Ensure all files have consistent column names")
        print("   - Update models/feature_config.json with actual feature names")

if __name__ == '__main__':
    main()
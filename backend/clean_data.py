#!/usr/bin/env python3
"""
Clean the CSV files by removing string label columns
"""
import pandas as pd
import os

def clean_csv_file(input_path, output_path):
    """Clean a CSV file by removing non-numeric label columns"""
    df = pd.read_csv(input_path)
    
    print(f"\nOriginal: {input_path}")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    
    # Identify columns that might be labels (not features)
    # These are typically string columns with the category name
    columns_to_drop = []
    
    for col in df.columns:
        # Check if column contains string labels like 'Athletic', 'Diver', etc.
        if df[col].dtype == 'object':
            unique_vals = df[col].unique()
            if len(unique_vals) == 1:  # If all values are the same (like 'Athletic')
                print(f"  Found label column: {col} = {unique_vals[0]}")
                columns_to_drop.append(col)
    
    # Keep only numeric columns and target
    if 'target' in df.columns:
        columns_to_keep = [col for col in df.columns if df[col].dtype in ['int64', 'float64'] or col == 'target']
    else:
        columns_to_keep = [col for col in df.columns if df[col].dtype in ['int64', 'float64']]
    
    df_clean = df[columns_to_keep]
    
    print(f"  Dropped columns: {columns_to_drop}")
    print(f"  Clean shape: {df_clean.shape}")
    print(f"  Clean columns: {list(df_clean.columns)}")
    
    # Save cleaned file
    df_clean.to_csv(output_path, index=False)
    print(f"  Saved to: {output_path}")
    
    return df_clean

def main():
    """Clean all CSV files"""
    categories = ['athletic', 'diver', 'typical']
    
    for category in categories:
        input_file = f'data/processed/{category}.csv'
        output_file = f'data/processed/{category}_clean.csv'
        
        if os.path.exists(input_file):
            clean_csv_file(input_file, output_file)
            
            # Also create a backup of original
            backup_file = f'data/processed/{category}_original.csv'
            if not os.path.exists(backup_file):
                import shutil
                shutil.copy2(input_file, backup_file)
                print(f"  Backup saved: {backup_file}")
    
    print("\n✓ Cleaning complete!")
    print("\nNext steps:")
    print("1. Check the cleaned files: data/processed/*_clean.csv")
    print("2. Run setup again: python3 setup.py")
    print("3. Or manually rename: mv athletic_clean.csv athletic.csv")

if __name__ == '__main__':
    main()
import pandas as pd
import os
from pathlib import Path

def calculate_averages():
  
    data_dir = Path('results/data')
    output_file = Path('results/processedDatas.csv')
    
    results = []
    
    csv_files = sorted(data_dir.glob('*.csv'))
        
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            
            if 'Delta' in df.columns and 'CPU_ENERGY (J)' in df.columns:
                delta = df['Delta'].mean()
                cpu_energy = df['CPU_ENERGY (J)'].mean()
                
                results.append({
                    'Experiment Name': csv_file.stem,  
                    'Delta': delta,
                    'CPU_Energy (J)': cpu_energy
                })
                
                # print(f"Processed: {csv_file.name}")
            else:
                print("oops smth went wrong")
                
        except Exception as e:
            print(f"Error processing {csv_file.name}: {e}")
    
    results_df = pd.DataFrame(results)
    
    results_df.to_csv(output_file, index=False)
    print(f"\nResults saved to {output_file}")
    print(f"checking if all the csv files were used = {len(results)}")

calculate_averages()

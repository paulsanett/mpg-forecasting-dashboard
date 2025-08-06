#!/usr/bin/env python3
"""
Simple CSV Reader - No filtering, gets ALL data for enhanced modeling
"""

import csv
import sys
from datetime import datetime
from typing import List, Dict, Optional

class SimpleCSVReader:
    def __init__(self, filename='HIstoric Booking Data.csv'):
        self.filename = filename
        self.data = None
    
    def read_all_data(self) -> List[Dict]:
        """Read ALL data without filtering"""
        print("📁 READING ALL CSV DATA (NO FILTERING)")
        print("=" * 50)
        
        try:
            with open(self.filename, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader)
                
                print(f"📋 Total columns: {len(headers)}")
                
                # Column mappings based on user specification
                column_map = {
                    0: 'date',                    # Date
                    1: 'day_of_week',            # Day of Week
                    6: 'gpn_units',              # G - Grant Park North Units
                    7: 'gpn_revenue',            # H - Grant Park North Revenue
                    12: 'gps_units',             # M - Grant Park South Units
                    13: 'gps_revenue',           # N - Grant Park South Revenue
                    18: 'lakeside_units',        # S - Lakeside Units
                    19: 'lakeside_revenue',      # T - Lakeside Revenue
                    24: 'millennium_units',      # Y - Millennium Park Units
                    25: 'millennium_revenue',    # Z - Millennium Park Revenue
                    26: 'online_units',          # AA - Online Units
                    27: 'online_revenue',        # AB - Online Revenue
                    31: 'total_units',           # AF - Total Units
                    35: 'total_revenue',         # AJ - Total Revenue
                    39: 'avg_reservation_value', # AN - Average Reservation Value
                    44: 'gas_price',             # AS - Gas Price
                    45: 'notes'                  # AT - Notes
                }
                
                all_records = []
                row_count = 0
                
                for row in reader:
                    row_count += 1
                    
                    if len(row) < 46:  # Skip incomplete rows
                        continue
                    
                    # Create record with all available data
                    record = {}
                    
                    for col_idx, field_name in column_map.items():
                        if col_idx < len(row):
                            raw_value = row[col_idx].strip()
                            
                            # Parse different data types
                            if field_name in ['date']:
                                record[field_name] = raw_value
                            elif field_name in ['day_of_week', 'notes']:
                                record[field_name] = raw_value
                            elif 'revenue' in field_name or field_name == 'gas_price' or field_name == 'avg_reservation_value':
                                # Parse currency/numeric values
                                try:
                                    if raw_value and raw_value != '-':
                                        clean_value = raw_value.replace('$', '').replace(',', '').strip()
                                        if clean_value:
                                            record[field_name] = float(clean_value)
                                        else:
                                            record[field_name] = 0.0
                                    else:
                                        record[field_name] = 0.0
                                except ValueError:
                                    record[field_name] = 0.0
                            elif 'units' in field_name:
                                # Parse unit counts
                                try:
                                    if raw_value and raw_value != '-':
                                        clean_value = raw_value.replace(',', '').strip()
                                        if clean_value:
                                            record[field_name] = int(float(clean_value))
                                        else:
                                            record[field_name] = 0
                                    else:
                                        record[field_name] = 0
                                except ValueError:
                                    record[field_name] = 0
                            else:
                                record[field_name] = raw_value
                    
                    all_records.append(record)
                
                print(f"✅ Loaded {len(all_records)} total records (no filtering)")
                
                # Analyze data quality
                self._analyze_data_quality(all_records)
                
                self.data = all_records
                return all_records
                
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            return []
    
    def _analyze_data_quality(self, records):
        """Analyze data quality without filtering"""
        print(f"\n📊 DATA QUALITY ANALYSIS:")
        print("-" * 30)
        
        # Count valid data by field
        field_counts = {}
        
        for field in ['total_revenue', 'gas_price', 'avg_reservation_value', 'notes']:
            count = 0
            values = []
            
            for record in records:
                value = record.get(field, 0)
                if field == 'notes':
                    if value and str(value).strip() and str(value).strip() != '-':
                        count += 1
                        values.append(str(value)[:50])
                elif isinstance(value, (int, float)) and value > 0:
                    count += 1
                    values.append(value)
            
            field_counts[field] = count
            
            print(f"   {field}: {count}/{len(records)} records ({count/len(records)*100:.1f}%)")
            
            if field == 'gas_price' and count > 0:
                print(f"      Range: ${min(values):.2f} - ${max(values):.2f}")
                print(f"      Average: ${sum(values)/len(values):.2f}")
            elif field == 'total_revenue' and count > 0:
                print(f"      Range: ${min(values):,.0f} - ${max(values):,.0f}")
                print(f"      Average: ${sum(values)/len(values):,.0f}")
            elif field == 'avg_reservation_value' and count > 0:
                print(f"      Range: ${min(values):.2f} - ${max(values):.2f}")
                print(f"      Average: ${sum(values)/len(values):.2f}")
        
        # Count records with both revenue and gas price
        both_count = 0
        for record in records:
            if record.get('total_revenue', 0) > 0 and record.get('gas_price', 0) > 0:
                both_count += 1
        
        print(f"   Revenue + Gas Price: {both_count}/{len(records)} records ({both_count/len(records)*100:.1f}%)")
        
        if both_count > 1000:
            print("   ✅ EXCELLENT! Sufficient data for enhanced modeling")
        elif both_count > 100:
            print("   👍 GOOD! Adequate data for modeling")
        else:
            print("   ⚠️  Limited data for enhanced modeling")
    
    def get_modeling_data(self) -> List[Dict]:
        """Get records suitable for modeling (with revenue and predictors)"""
        if not self.data:
            self.read_all_data()
        
        modeling_records = []
        
        for record in self.data:
            # Must have revenue
            if record.get('total_revenue', 0) <= 0:
                continue
            
            # Must have at least one predictor
            has_predictor = (
                record.get('gas_price', 0) > 0 or
                record.get('avg_reservation_value', 0) > 0 or
                (record.get('notes', '') and str(record.get('notes', '')).strip() != '-')
            )
            
            if has_predictor:
                modeling_records.append(record)
        
        print(f"📊 Modeling dataset: {len(modeling_records)} records with revenue + predictors")
        return modeling_records

def main():
    """Test the simple CSV reader"""
    reader = SimpleCSVReader()
    data = reader.read_all_data()
    
    if data:
        print(f"\n🎉 SUCCESS! Loaded {len(data)} total records")
        
        modeling_data = reader.get_modeling_data()
        print(f"📈 Ready for modeling with {len(modeling_data)} enhanced records")
        
        return True
    else:
        print("❌ Failed to load data")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

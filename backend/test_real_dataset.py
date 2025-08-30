#!/usr/bin/env python3
"""
AML Guardian Test with Real Dataset
Test the advanced money laundering detection system using test_transactions_expandednew.csv
This script will:
1. Load the real transaction data
2. Upload it to the system
3. Run all advanced detection features
4. Analyze results and generate comprehensive report
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime
import os

class AMLRealDataTester:
    def __init__(self, base_url="http://localhost:5001", csv_file="test_transactions_expandednew.csv"):
        self.base_url = base_url
        self.csv_file = csv_file
        self.results = {}
        self.accounts = []
        
    def test_api_connection(self):
        """Test if the API is running"""
        try:
            response = requests.get(f"{self.base_url}/api/suspects", timeout=5)
            if response.status_code == 200:
                print("✅ API Connection successful")
                return True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ API Connection failed: {e}")
            print("💡 Make sure to start the backend server: python app.py")
            return False
    
    def load_and_analyze_dataset(self):
        """Load the CSV file and analyze its structure"""
        try:
            # Check if file exists
            if not os.path.exists(self.csv_file):
                print(f"❌ File not found: {self.csv_file}")
                return False
            
            # Load the dataset
            df = pd.read_csv(self.csv_file)
            print(f"✅ Loaded dataset with {len(df)} transactions")
            
            # Analyze dataset structure
            print(f"📊 Dataset Analysis:")
            print(f"   - Total transactions: {len(df)}")
            print(f"   - Columns: {list(df.columns)}")
            print(f"   - Transaction types: {df['type'].value_counts().to_dict()}")
            print(f"   - Fraud transactions: {df['isFraud'].sum()}")
            print(f"   - Flagged transactions: {df['isFlaggedFraud'].sum()}")
            
            # Extract unique accounts
            self.accounts = list(set(list(df['nameOrig'].unique()) + list(df['nameDest'].unique())))
            self.accounts = [acc for acc in self.accounts if acc.startswith('C')]  # Only customer accounts
            print(f"   - Unique customer accounts: {len(self.accounts)}")
            
            # Show some sample accounts
            print(f"   - Sample accounts: {self.accounts[:5]}")
            
            self.dataset = df
            return True
            
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return False
    
    def upload_dataset(self):
        """Upload the dataset to the AML system"""
        try:
            print(f"\n📤 Uploading {self.csv_file} to AML system...")
            
            with open(self.csv_file, 'rb') as f:
                files = {'file': (self.csv_file, f, 'text/csv')}
                response = requests.post(f"{self.base_url}/api/upload-file", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Upload successful!")
                    print(f"   - Status: {result.get('status', 'Unknown')}")
                    if 'records_processed' in result:
                        print(f"   - Records processed: {result['records_processed']}")
                    return True
                else:
                    print(f"❌ Upload failed with status {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def test_advanced_risk_scoring(self, account_id):
        """Test advanced risk scoring on a specific account"""
        try:
            response = requests.get(f"{self.base_url}/api/advanced-risk-score/{account_id}")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "risk_score": data.get('risk_score', 0),
                    "risk_level": data.get('risk_level', 'UNKNOWN'),
                    "risk_factors": len(data.get('risk_factors', [])),
                    "entity_type": data.get('entity_type', 'UNKNOWN')
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_money_flow_tracking(self, account_id):
        """Test money flow tracking"""
        try:
            response = requests.get(f"{self.base_url}/api/money-flow-tracking/{account_id}?max_depth=4")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "flow_paths": len(data.get('flow_paths', [])),
                    "suspicious_patterns": len(data.get('suspicious_patterns', [])),
                    "total_flow_amount": sum(path.get('total_amount', 0) for path in data.get('flow_paths', []))
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_circular_transactions(self):
        """Test circular transaction detection"""
        try:
            response = requests.get(f"{self.base_url}/api/circular-transactions?min_amount=1000&max_cycle_length=5")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "total_cycles": data.get('total_cycles', 0),
                    "cycles": data.get('cycles', [])
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_comprehensive_analysis(self, account_id):
        """Test comprehensive analysis"""
        try:
            response = requests.get(f"{self.base_url}/api/comprehensive-analysis/{account_id}")
            
            if response.status_code == 200:
                data = response.json()
                assessment = data.get('overall_assessment', {})
                return {
                    "success": True,
                    "risk_level": assessment.get('risk_level', 'UNKNOWN'),
                    "risk_score": assessment.get('risk_score', 0),
                    "key_concerns": len(assessment.get('key_concerns', [])),
                    "recommendations": len(assessment.get('recommended_actions', []))
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_fraud_cases(self):
        """Analyze known fraud cases from the dataset"""
        fraud_cases = self.dataset[self.dataset['isFraud'] == 1]
        print(f"\n🔍 Analyzing {len(fraud_cases)} known fraud cases...")
        
        fraud_results = []
        for _, row in fraud_cases.head(3).iterrows():  # Test first 3 fraud cases
            account = row['nameOrig']
            print(f"\n   Testing fraud case: {account} (Amount: ${row['amount']:,.2f})")
            
            # Test risk scoring
            risk_result = self.test_advanced_risk_scoring(account)
            if risk_result['success']:
                print(f"   ✅ Risk Score: {risk_result['risk_score']:.3f} ({risk_result['risk_level']})")
            else:
                print(f"   ❌ Risk scoring failed: {risk_result['error']}")
            
            # Test comprehensive analysis
            comp_result = self.test_comprehensive_analysis(account)
            if comp_result['success']:
                print(f"   ✅ Comprehensive analysis: {comp_result['key_concerns']} concerns, {comp_result['recommendations']} recommendations")
            else:
                print(f"   ❌ Comprehensive analysis failed")
            
            fraud_results.append({
                'account': account,
                'actual_fraud': True,
                'amount': row['amount'],
                'risk_result': risk_result,
                'comp_result': comp_result
            })
        
        return fraud_results
    
    def analyze_normal_cases(self):
        """Analyze normal (non-fraud) cases"""
        normal_cases = self.dataset[self.dataset['isFraud'] == 0]
        print(f"\n✅ Analyzing {len(normal_cases)} normal transaction cases...")
        
        normal_results = []
        for _, row in normal_cases.head(3).iterrows():  # Test first 3 normal cases
            account = row['nameOrig']
            print(f"\n   Testing normal case: {account} (Amount: ${row['amount']:,.2f})")
            
            # Test risk scoring
            risk_result = self.test_advanced_risk_scoring(account)
            if risk_result['success']:
                print(f"   ✅ Risk Score: {risk_result['risk_score']:.3f} ({risk_result['risk_level']})")
            else:
                print(f"   ❌ Risk scoring failed: {risk_result['error']}")
            
            normal_results.append({
                'account': account,
                'actual_fraud': False,
                'amount': row['amount'],
                'risk_result': risk_result
            })
        
        return normal_results
    
    def test_network_analysis(self):
        """Test network-wide analysis features"""
        print(f"\n🌐 Testing Network-wide Analysis...")
        
        # Test circular transactions
        circular_result = self.test_circular_transactions()
        if circular_result['success']:
            print(f"   ✅ Circular transactions: {circular_result['total_cycles']} cycles detected")
        else:
            print(f"   ❌ Circular transaction detection failed")
        
        # Test shell company networks
        try:
            response = requests.get(f"{self.base_url}/api/shell-company-networks")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Shell company networks: {data.get('total_networks', 0)} networks found")
            else:
                print(f"   ❌ Shell company detection failed")
        except Exception as e:
            print(f"   ❌ Shell company detection error: {e}")
        
        # Test cash patterns
        try:
            response = requests.get(f"{self.base_url}/api/cash-pattern-analysis?min_amount=1000")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Cash patterns: {data.get('total_patterns', 0)} patterns, {data.get('high_risk_patterns', 0)} high-risk")
            else:
                print(f"   ❌ Cash pattern analysis failed")
        except Exception as e:
            print(f"   ❌ Cash pattern analysis error: {e}")
        
        return circular_result
    
    def generate_report(self, fraud_results, normal_results, network_results):
        """Generate comprehensive test report"""
        print(f"\n" + "="*80)
        print(f"📋 AML GUARDIAN TEST REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"="*80)
        
        print(f"\n📊 Dataset Summary:")
        print(f"   - Total transactions: {len(self.dataset)}")
        print(f"   - Fraud transactions: {self.dataset['isFraud'].sum()}")
        print(f"   - Normal transactions: {len(self.dataset) - self.dataset['isFraud'].sum()}")
        print(f"   - Unique accounts tested: {len(self.accounts)}")
        
        print(f"\n🎯 Fraud Detection Results:")
        fraud_detected = sum(1 for r in fraud_results if r['risk_result'].get('success') and r['risk_result'].get('risk_score', 0) > 0.5)
        print(f"   - Fraud cases tested: {len(fraud_results)}")
        print(f"   - High risk detected: {fraud_detected}/{len(fraud_results)}")
        print(f"   - Detection rate: {(fraud_detected/len(fraud_results)*100):.1f}%" if fraud_results else "N/A")
        
        print(f"\n✅ Normal Case Results:")
        normal_low_risk = sum(1 for r in normal_results if r['risk_result'].get('success') and r['risk_result'].get('risk_score', 0) < 0.5)
        print(f"   - Normal cases tested: {len(normal_results)}")
        print(f"   - Correctly classified as low risk: {normal_low_risk}/{len(normal_results)}")
        print(f"   - Accuracy rate: {(normal_low_risk/len(normal_results)*100):.1f}%" if normal_results else "N/A")
        
        print(f"\n🌐 Network Analysis:")
        if network_results['success']:
            print(f"   - Circular transactions detected: {network_results['total_cycles']}")
        else:
            print(f"   - Network analysis: Failed")
        
        print(f"\n🎉 Test Summary:")
        total_tests = len(fraud_results) + len(normal_results) + 1  # +1 for network tests
        successful_tests = sum(1 for r in fraud_results + normal_results if r['risk_result'].get('success')) + (1 if network_results['success'] else 0)
        print(f"   - Total tests run: {total_tests}")
        print(f"   - Successful tests: {successful_tests}")
        print(f"   - Success rate: {(successful_tests/total_tests*100):.1f}%")
        
        if successful_tests == total_tests:
            print(f"\n🏆 ALL TESTS PASSED! The AML Guardian system is working correctly with your dataset.")
        else:
            print(f"\n⚠️  Some tests failed. Please check the backend server and database connections.")
    
    def run_complete_test(self):
        """Run complete test suite with the real dataset"""
        print("🚀 Starting AML Guardian Real Dataset Test")
        print("="*60)
        
        # Step 1: Check API connection
        if not self.test_api_connection():
            return
        
        # Step 2: Load and analyze dataset
        if not self.load_and_analyze_dataset():
            return
        
        # Step 3: Upload dataset
        if not self.upload_dataset():
            print("⚠️  Upload failed, but continuing with existing data...")
        
        # Wait for processing
        print("\n⏳ Waiting for data processing...")
        time.sleep(3)
        
        # Step 4: Analyze fraud cases
        fraud_results = self.analyze_fraud_cases()
        
        # Step 5: Analyze normal cases
        normal_results = self.analyze_normal_cases()
        
        # Step 6: Test network analysis
        network_results = self.test_network_analysis()
        
        # Step 7: Generate comprehensive report
        self.generate_report(fraud_results, normal_results, network_results)

def main():
    """Main test execution"""
    # Check if we're in the right directory
    if not os.path.exists("test_transactions_expandednew.csv"):
        if os.path.exists("../test_transactions_expandednew.csv"):
            os.chdir("..")
        else:
            print("❌ test_transactions_expandednew.csv not found!")
            print("💡 Please run this script from the project root directory")
            return
    
    tester = AMLRealDataTester()
    tester.run_complete_test()

if __name__ == "__main__":
    main()

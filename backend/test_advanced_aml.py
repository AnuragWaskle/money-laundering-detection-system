#!/usr/bin/env python3
"""
Advanced AML Guardian Test Suite
Tests the enhanced money laundering detection capabilities including:
- Multi-account money flow tracking
- Offshore account detection
- Shell company network identification
- Circular transaction detection
- Advanced risk scoring with 7-factor analysis
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import random

class AMLAdvancedTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.test_accounts = []
        self.test_results = {}
        
    def test_connection(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{self.base_url}/api/suspects", timeout=5)
            print(f"✅ API Connection: {response.status_code}")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"❌ API Connection Failed: {e}")
            return False
    
    def create_test_data(self):
        """Create test transaction data for advanced testing"""
        print("\n🔧 Creating test transaction data...")
        
        # Generate test accounts
        self.test_accounts = [
            f"ACC_{str(i).zfill(6)}" for i in range(1, 21)
        ]
        
        # Create test transactions with suspicious patterns
        transactions = []
        
        # 1. Normal transactions
        for i in range(100):
            transactions.append({
                "transaction_id": f"TXN_{str(i+1).zfill(6)}",
                "account_from": random.choice(self.test_accounts[:10]),
                "account_to": random.choice(self.test_accounts[:10]),
                "amount": random.uniform(100, 5000),
                "transaction_type": random.choice(["TRANSFER", "DEPOSIT", "WITHDRAWAL"]),
                "timestamp": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "description": "Regular transaction"
            })
        
        # 2. Circular transaction pattern
        circular_accounts = self.test_accounts[10:15]
        for i, account in enumerate(circular_accounts):
            next_account = circular_accounts[(i + 1) % len(circular_accounts)]
            transactions.append({
                "transaction_id": f"CIRC_{str(i+1).zfill(3)}",
                "account_from": account,
                "account_to": next_account,
                "amount": 25000.00,
                "transaction_type": "TRANSFER",
                "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                "description": "Circular flow transaction"
            })
        
        # 3. Layering scheme pattern
        layering_accounts = self.test_accounts[15:20]
        for i in range(len(layering_accounts) - 1):
            transactions.append({
                "transaction_id": f"LAYER_{str(i+1).zfill(3)}",
                "account_from": layering_accounts[i],
                "account_to": layering_accounts[i + 1],
                "amount": 100000.00 - (i * 1000),
                "transaction_type": "TRANSFER",
                "timestamp": (datetime.now() - timedelta(minutes=i*30)).isoformat(),
                "description": "Layering transaction"
            })
        
        # 4. High-velocity transactions
        velocity_account = self.test_accounts[0]
        for i in range(20):
            transactions.append({
                "transaction_id": f"VELOCITY_{str(i+1).zfill(3)}",
                "account_from": velocity_account,
                "account_to": random.choice(self.test_accounts[1:5]),
                "amount": random.uniform(50000, 150000),
                "transaction_type": "TRANSFER",
                "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                "description": "High velocity transaction"
            })
        
        # 5. Cash-intensive transactions
        cash_account = self.test_accounts[5]
        for i in range(10):
            transactions.append({
                "transaction_id": f"CASH_{str(i+1).zfill(3)}",
                "account_from": cash_account,
                "account_to": "CASH_OUT",
                "amount": random.uniform(15000, 25000),
                "transaction_type": "CASH_WITHDRAWAL",
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "description": "Cash withdrawal"
            })
        
        print(f"✅ Generated {len(transactions)} test transactions")
        return transactions
    
    def upload_test_data(self, transactions):
        """Upload test data to the system"""
        print("\n📤 Uploading test data...")
        
        # Create CSV file
        df = pd.DataFrame(transactions)
        csv_file = "test_advanced_transactions.csv"
        df.to_csv(csv_file, index=False)
        
        # Upload file
        try:
            with open(csv_file, 'rb') as f:
                files = {'file': (csv_file, f, 'text/csv')}
                response = requests.post(f"{self.base_url}/api/upload-file", files=files)
                
                if response.status_code == 200:
                    print("✅ Test data uploaded successfully")
                    return True
                else:
                    print(f"❌ Upload failed: {response.text}")
                    return False
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def test_advanced_risk_scoring(self):
        """Test advanced risk scoring functionality"""
        print("\n🎯 Testing Advanced Risk Scoring...")
        
        test_account = self.test_accounts[0]  # High-velocity account
        
        try:
            response = requests.get(f"{self.base_url}/api/advanced-risk-score/{test_account}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Risk Score: {data.get('risk_score', 'N/A')}")
                print(f"✅ Risk Level: {data.get('risk_level', 'N/A')}")
                print(f"✅ Risk Factors: {len(data.get('risk_factors', []))}")
                self.test_results['risk_scoring'] = True
                return data
            else:
                print(f"❌ Risk scoring failed: {response.text}")
                self.test_results['risk_scoring'] = False
                return None
        except Exception as e:
            print(f"❌ Risk scoring error: {e}")
            self.test_results['risk_scoring'] = False
            return None
    
    def test_money_flow_tracking(self):
        """Test money flow tracking functionality"""
        print("\n💰 Testing Money Flow Tracking...")
        
        test_account = self.test_accounts[15]  # Layering account
        
        try:
            response = requests.get(f"{self.base_url}/api/money-flow-tracking/{test_account}?max_depth=5")
            
            if response.status_code == 200:
                data = response.json()
                flow_paths = data.get('flow_paths', [])
                suspicious_patterns = data.get('suspicious_patterns', [])
                
                print(f"✅ Flow Paths Found: {len(flow_paths)}")
                print(f"✅ Suspicious Patterns: {len(suspicious_patterns)}")
                self.test_results['money_flow'] = True
                return data
            else:
                print(f"❌ Money flow tracking failed: {response.text}")
                self.test_results['money_flow'] = False
                return None
        except Exception as e:
            print(f"❌ Money flow tracking error: {e}")
            self.test_results['money_flow'] = False
            return None
    
    def test_layering_detection(self):
        """Test layering scheme detection"""
        print("\n🔄 Testing Layering Detection...")
        
        test_account = self.test_accounts[15]  # Layering account
        
        try:
            response = requests.get(f"{self.base_url}/api/layering-detection/{test_account}")
            
            if response.status_code == 200:
                data = response.json()
                cycles_detected = data.get('cycles_detected', 0)
                layering_indicators = data.get('layering_indicators', [])
                
                print(f"✅ Cycles Detected: {cycles_detected}")
                print(f"✅ Layering Indicators: {len(layering_indicators)}")
                self.test_results['layering_detection'] = True
                return data
            else:
                print(f"❌ Layering detection failed: {response.text}")
                self.test_results['layering_detection'] = False
                return None
        except Exception as e:
            print(f"❌ Layering detection error: {e}")
            self.test_results['layering_detection'] = False
            return None
    
    def test_circular_transactions(self):
        """Test circular transaction detection"""
        print("\n🔄 Testing Circular Transaction Detection...")
        
        try:
            response = requests.get(f"{self.base_url}/api/circular-transactions?min_amount=20000&max_cycle_length=6")
            
            if response.status_code == 200:
                data = response.json()
                total_cycles = data.get('total_cycles', 0)
                cycles = data.get('cycles', [])
                
                print(f"✅ Total Cycles Found: {total_cycles}")
                print(f"✅ Cycle Details: {len(cycles)} records")
                self.test_results['circular_transactions'] = True
                return data
            else:
                print(f"❌ Circular transaction detection failed: {response.text}")
                self.test_results['circular_transactions'] = False
                return None
        except Exception as e:
            print(f"❌ Circular transaction detection error: {e}")
            self.test_results['circular_transactions'] = False
            return None
    
    def test_shell_company_networks(self):
        """Test shell company network detection"""
        print("\n🏢 Testing Shell Company Network Detection...")
        
        try:
            response = requests.get(f"{self.base_url}/api/shell-company-networks")
            
            if response.status_code == 200:
                data = response.json()
                total_networks = data.get('total_networks', 0)
                networks = data.get('networks', [])
                
                print(f"✅ Networks Found: {total_networks}")
                print(f"✅ Network Analysis: {len(networks)} records")
                self.test_results['shell_companies'] = True
                return data
            else:
                print(f"❌ Shell company detection failed: {response.text}")
                self.test_results['shell_companies'] = False
                return None
        except Exception as e:
            print(f"❌ Shell company detection error: {e}")
            self.test_results['shell_companies'] = False
            return None
    
    def test_cash_pattern_analysis(self):
        """Test cash pattern analysis"""
        print("\n💵 Testing Cash Pattern Analysis...")
        
        try:
            response = requests.get(f"{self.base_url}/api/cash-pattern-analysis?min_amount=10000")
            
            if response.status_code == 200:
                data = response.json()
                total_patterns = data.get('total_patterns', 0)
                high_risk_patterns = data.get('high_risk_patterns', 0)
                
                print(f"✅ Cash Patterns Found: {total_patterns}")
                print(f"✅ High Risk Patterns: {high_risk_patterns}")
                self.test_results['cash_patterns'] = True
                return data
            else:
                print(f"❌ Cash pattern analysis failed: {response.text}")
                self.test_results['cash_patterns'] = False
                return None
        except Exception as e:
            print(f"❌ Cash pattern analysis error: {e}")
            self.test_results['cash_patterns'] = False
            return None
    
    def test_comprehensive_analysis(self):
        """Test comprehensive analysis functionality"""
        print("\n📊 Testing Comprehensive Analysis...")
        
        test_account = self.test_accounts[0]  # High-velocity account
        
        try:
            response = requests.get(f"{self.base_url}/api/comprehensive-analysis/{test_account}")
            
            if response.status_code == 200:
                data = response.json()
                overall_assessment = data.get('overall_assessment', {})
                
                print(f"✅ Risk Level: {overall_assessment.get('risk_level', 'N/A')}")
                print(f"✅ Risk Score: {overall_assessment.get('risk_score', 'N/A')}")
                print(f"✅ Key Concerns: {len(overall_assessment.get('key_concerns', []))}")
                print(f"✅ Recommendations: {len(overall_assessment.get('recommended_actions', []))}")
                self.test_results['comprehensive_analysis'] = True
                return data
            else:
                print(f"❌ Comprehensive analysis failed: {response.text}")
                self.test_results['comprehensive_analysis'] = False
                return None
        except Exception as e:
            print(f"❌ Comprehensive analysis error: {e}")
            self.test_results['comprehensive_analysis'] = False
            return None
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting AML Guardian Advanced Test Suite")
        print("=" * 60)
        
        # Check API connection
        if not self.test_connection():
            print("❌ Cannot connect to API. Make sure the backend is running.")
            return
        
        # Create and upload test data
        transactions = self.create_test_data()
        if not self.upload_test_data(transactions):
            print("❌ Cannot upload test data. Some tests may fail.")
        
        # Wait for data processing
        print("\n⏳ Waiting for data processing...")
        time.sleep(5)
        
        # Run all tests
        self.test_advanced_risk_scoring()
        self.test_money_flow_tracking()
        self.test_layering_detection()
        self.test_circular_transactions()
        self.test_shell_company_networks()
        self.test_cash_pattern_analysis()
        self.test_comprehensive_analysis()
        
        # Summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📋 Test Results Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print("-" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! Advanced AML detection system is working correctly.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} tests failed. Please check the implementation.")

def main():
    """Main test execution"""
    tester = AMLAdvancedTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()

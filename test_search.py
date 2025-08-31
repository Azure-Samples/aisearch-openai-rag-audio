#!/usr/bin/env python3
"""
سكريبت لاختبار Azure AI Search مباشرة
"""
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from dotenv import load_dotenv

async def test_search():
    # تحميل الإعدادات
    load_dotenv("app/backend/.env")
    
    # معلومات الاتصال
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX") 
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")
    
    print(f"🔍 اختبار Azure Search:")
    print(f"   Endpoint: {search_endpoint}")
    print(f"   Index: {search_index}")
    print(f"   Key: {search_key[:10]}...")
    
    # إنشاء عميل البحث
    search_client = SearchClient(
        search_endpoint, 
        search_index, 
        AzureKeyCredential(search_key)
    )
    
    print("\n📊 اختبار البحث العام...")
    try:
        # بحث عام للحصول على جميع البيانات
        search_results = await search_client.search(
            search_text="*",  # البحث عن كل شيء
            top=10,
            select="*"  # جلب جميع الحقول
        )
        
        result_count = 0
        async for result in search_results:
            result_count += 1
            print(f"\n--- النتيجة {result_count} ---")
            for key, value in result.items():
                print(f"  {key}: {value}")
        
        if result_count == 0:
            print("❌ لا توجد بيانات في الفهرس!")
        else:
            print(f"\n✅ تم العثور على {result_count} سجل(ات)")
            
    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")
    
    print("\n🍕 اختبار البحث عن البيتزا...")
    try:
        # بحث محدد عن البيتزا
        search_results = await search_client.search(
            search_text="pizza",
            top=5,
            select="*"
        )
        
        result_count = 0
        async for result in search_results:
            result_count += 1
            print(f"\n--- نتيجة البيتزا {result_count} ---")
            for key, value in result.items():
                print(f"  {key}: {value}")
        
        if result_count == 0:
            print("❌ لم يتم العثور على بيتزا!")
        else:
            print(f"\n✅ تم العثور على {result_count} نوع(أ) من البيتزا")
            
    except Exception as e:
        print(f"❌ خطأ في البحث عن البيتزا: {e}")
    
    await search_client.close()

if __name__ == "__main__":
    asyncio.run(test_search())

import asyncio
import os
from dotenv import load_dotenv
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential

# تحديد مسار ملف .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

async def test_specific_search():
    # تحقق من المتغيرات
    service_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
    api_key = os.getenv('AZURE_SEARCH_API_KEY')
    index_name = os.getenv('AZURE_SEARCH_INDEX')

    print(f"🔗 Service endpoint: {service_endpoint}")
    print(f"📇 Index name: {index_name}")
    print(f"🔑 API key: {'***' + api_key[-4:] if api_key else 'None'}")

    if not all([service_endpoint, api_key, index_name]):
        print("❌ Missing required environment variables!")
        return

    # إنشاء العميل
    search_client = SearchClient(
        endpoint=service_endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key)
    )

    try:
        print("\n🧪 اختبار البحث بالبيانات الجديدة:")
        
        # اختبارات للبيانات المحددة التي أعطاها المستخدم
        test_queries = [
            "كالزونى فراخ كرسبي",
            "كالزونى فراخ باربكيو", 
            "اونيون رينج",
            "تشيزي كرسبي",
            "فراخ",
            "باربكيو",
            "كرسبي",
            "كالزونى"
        ]
        
        for query in test_queries:
            print(f"\n🔍 البحث عن: '{query}'")
            
            search_results = await search_client.search(
                search_text=query,
                query_type="simple",
                top=5,
                select="ID,Name,ingredients,Price",
                search_mode="any"  # البحث عن أي كلمة من الكلمات المدخلة
            )
            
            result_count = 0
            async for result in search_results:
                result_count += 1
                print(f"  ✅ النتيجة {result_count}:")
                print(f"     🆔 ID: {result.get('ID', 'N/A')}")
                print(f"     🍽️ Name: {result.get('Name', 'N/A')}")
                print(f"     💰 Price: {result.get('Price', 'N/A')} جنيه")
                print(f"     🧾 ingredients: {result.get('ingredients', 'N/A')}")
                print("     ---")
            
            if result_count == 0:
                print(f"  ❌ لا توجد نتائج للبحث عن '{query}'")
            else:
                print(f"  🎯 وجدت {result_count} نتائج")

        # اختبار شامل لجلب كل البيانات
        print(f"\n📋 اختبار عرض جميع البيانات:")
        search_results = await search_client.search(
            search_text="*",
            query_type="simple", 
            top=50,
            select="ID,Name,ingredients,Price",
            order_by=["ID"]
        )
        
        print("📝 جميع البيانات في الفهرس:")
        result_count = 0
        async for result in search_results:
            result_count += 1
            print(f"  {result_count}. [ID:{result.get('ID')}] {result.get('Name')} - {result.get('Price')} جنيه")
        
        print(f"\n📊 إجمالي العناصر في الفهرس: {result_count}")

    except Exception as e:
        print(f"❌ خطأ في البحث: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await search_client.close()

if __name__ == "__main__":
    asyncio.run(test_specific_search())

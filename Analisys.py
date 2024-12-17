import requests


def send_image_to_plantnet(image_file, api_key):
    url = "https://my-api.plantnet.org/v2/identify/all"
    files = {
        'images': (image_file.name, image_file, 'image/jpeg')
    }
    params = {
        'api-key': api_key,
        'include-related-images': 'false',
        'nb-results': 1
    }

    try:
        response = requests.post(url, files=files, params=params)
        if response.status_code == 200:
            data = response.json()
            best_result = data['results'][0]
            species = best_result.get('species', {})
            return {
                "scientific_name": species.get('scientificName', 'غير متوفر'),
                "common_names": species.get('commonNames', ['غير متوفر']),
                "score": f"{best_result.get('score', 0.0) * 100:.2f}",
                "genus": species.get('genus', {}).get('scientificName', 'غير متوفر'),
                "family": species.get('family', {}).get('scientificName', 'غير متوفر')
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

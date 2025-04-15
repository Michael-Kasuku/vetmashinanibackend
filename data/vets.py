import requests
import random

# List of 47 counties in Kenya with their latitude and longitude
counties = [
    {'county': 'Nairobi', 'lat': -1.2921, 'lng': 36.8219},
    {'county': 'Mombasa', 'lat': -4.0435, 'lng': 39.6682},
    {'county': 'Kisumu', 'lat': -0.0917, 'lng': 34.7680},
    {'county': 'Nakuru', 'lat': -0.3031, 'lng': 36.0800},
    {'county': 'Eldoret', 'lat': 0.5155, 'lng': 35.2690},
    {'county': 'Thika', 'lat': -1.0331, 'lng': 37.0731},
    {'county': 'Kisii', 'lat': -0.6767, 'lng': 34.7680},
    {'county': 'Nyeri', 'lat': -0.4195, 'lng': 36.9500},
    {'county': 'Meru', 'lat': 0.0473, 'lng': 37.6410},
    {'county': 'Bomet', 'lat': -0.9142, 'lng': 35.0500},
    {'county': 'Garissa', 'lat': -0.4543, 'lng': 39.6615},
    {'county': 'Homa Bay', 'lat': -0.5364, 'lng': 34.8977},
    {'county': 'Isiolo', 'lat': 0.3501, 'lng': 37.5884},
    {'county': 'Kajiado', 'lat': -1.7004, 'lng': 36.7764},
    {'county': 'Kakamega', 'lat': 0.2834, 'lng': 34.7514},
    {'county': 'Kiambu', 'lat': -1.0167, 'lng': 36.9833},
    {'county': 'Kilifi', 'lat': -3.1214, 'lng': 39.9251},
    {'county': 'Kirinyaga', 'lat': -0.9499, 'lng': 37.2260},
    {'county': 'Kisumu', 'lat': -0.0917, 'lng': 34.7680},
    {'county': 'Kitui', 'lat': -1.3580, 'lng': 38.0204},
    {'county': 'Laikipia', 'lat': -0.0769, 'lng': 36.8580},
    {'county': 'Lamu', 'lat': -2.2630, 'lng': 40.5158},
    {'county': 'Machakos', 'lat': -1.5167, 'lng': 37.2878},
    {'county': 'Mandera', 'lat': 3.1428, 'lng': 41.8831},
    {'county': 'Marsabit', 'lat': 2.3378, 'lng': 37.9967},
    {'county': 'Meru', 'lat': 0.0473, 'lng': 37.6410},
    {'county': 'Migori', 'lat': -1.0667, 'lng': 34.5033},
    {'county': 'Mombasa', 'lat': -4.0435, 'lng': 39.6682},
    {'county': 'Murang’a', 'lat': -0.7167, 'lng': 37.2583},
    {'county': 'Nandi', 'lat': 0.1667, 'lng': 35.0475},
    {'county': 'Nakuru', 'lat': -0.3031, 'lng': 36.0800},
    {'county': 'Narok', 'lat': -1.0908, 'lng': 35.8172},
    {'county': 'Nyamira', 'lat': -0.5534, 'lng': 34.9660},
    {'county': 'Nyeri', 'lat': -0.4195, 'lng': 36.9500},
    {'county': 'Samburu', 'lat': 1.1598, 'lng': 36.5884},
    {'county': 'Siaya', 'lat': -0.0717, 'lng': 34.4365},
    {'county': 'Taita Taveta', 'lat': -3.4176, 'lng': 38.2027},
    {'county': 'Tana River', 'lat': -2.0011, 'lng': 39.6833},
    {'county': 'Tharaka Nithi', 'lat': -0.3975, 'lng': 37.6300},
    {'county': 'Trans Nzoia', 'lat': 1.0428, 'lng': 35.0208},
    {'county': 'Turkana', 'lat': 3.2892, 'lng': 35.6927},
    {'county': 'Uasin Gishu', 'lat': 0.5167, 'lng': 35.2690},
    {'county': 'Vihiga', 'lat': -0.0667, 'lng': 34.7313},
    {'county': 'Wajir', 'lat': 1.7500, 'lng': 40.0700},
    {'county': 'West Pokot', 'lat': 1.7271, 'lng': 35.1057},
    {'county': 'Nairobi', 'lat': -1.2921, 'lng': 36.8219}
]

# List of certified vet emails generated earlier
vet_emails = [
    'james.mutiso@vetmashinani.com', 'mary.mwangi@vetmashinani.com', 'john.njoroge@vetmashinani.com',
    'grace.kariuki@vetmashinani.com', 'david.ochieng@vetmashinani.com', 'lucy.otieno@vetmashinani.com',
    'michael.kamau@vetmashinani.com', 'alice.wangari@vetmashinani.com', 'stephen.kibaki@vetmashinani.com',
    'christine.akinyi@vetmashinani.com', 'daniel.mwania@vetmashinani.com', 'joyce.njiru@vetmashinani.com',
    'samuel.ruto@vetmashinani.com', 'faith.kibet@vetmashinani.com', 'joseph.ndungu@vetmashinani.com',
    'catherine.kimani@vetmashinani.com', 'paul.mwita@vetmashinani.com', 'hellen.kiplangat@vetmashinani.com',
    'brian.kariuki@vetmashinani.com', 'eunice.cheruiyot@vetmashinani.com', 'kevin.koech@vetmashinani.com',
    'esther.cherono@vetmashinani.com', 'peter.kangogo@vetmashinani.com', 'patricia.langat@vetmashinani.com',
    'daniel.chebet@vetmashinani.com', 'sarah.sang@vetmashinani.com', 'charles.kiptum@vetmashinani.com',
    'lydia.ngugi@vetmashinani.com', 'abraham.kariuki@vetmashinani.com', 'betty.chesang@vetmashinani.com',
    'victor.kisumu@vetmashinani.com', 'lillian.mbugua@vetmashinani.com', 'elvis.ngugi@vetmashinani.com',
    'sandra.obondo@vetmashinani.com', 'joshua.onyango@vetmashinani.com', 'monica.wamuyu@vetmashinani.com',
    'omar.chowdhury@vetmashinani.com', 'nina.juma@vetmashinani.com', 'dennis.kiptoo@vetmashinani.com',
    'grace.kihoro@vetmashinani.com', 'douglas.mutua@vetmashinani.com', 'caroline.kuria@vetmashinani.com',
    'felix.musyoka@vetmashinani.com', 'diana.mwangi@vetmashinani.com', 'richard.njenga@vetmashinani.com',
    'mary.njeri@vetmashinani.com', 'george.kamotho@vetmashinani.com', 'veronica.mumo@vetmashinani.com',
    'andrew.kilonzo@vetmashinani.com', 'sophia.achieng@vetmashinani.com', 'oscar.kithinji@vetmashinani.com',
    'nelly.odhiambo@vetmashinani.com', 'kennedy.ongaya@vetmashinani.com', 'isabel.karanja@vetmashinani.com',
    'cyrus.kimathi@vetmashinani.com', 'rose.odinga@vetmashinani.com', 'jacob.mwangi@vetmashinani.com',
    'hannah.kibuchi@vetmashinani.com', 'benjamin.maina@vetmashinani.com', 'nancy.gikonyo@vetmashinani.com',
    'paul.waweru@vetmashinani.com', 'ruth.mutava@vetmashinani.com', 'chris.ruto@vetmashinani.com',
    'jemima.ochieng@vetmashinani.com', 'raphael.riverson@vetmashinani.com', 'lily.mariga@vetmashinani.com',
    'david.ndirangu@vetmashinani.com', 'jennifer.njuguna@vetmashinani.com', 'tony.gichuki@vetmashinani.com',
    'grace.otieno@vetmashinani.com', 'moses.macharia@vetmashinani.com', 'rebecca.mwilu@vetmashinani.com',
    'gideon.mwangi@vetmashinani.com', 'dorcas.ndegwa@vetmashinani.com', 'sylvester.ngugi@vetmashinani.com',
    'damaris.nganga@vetmashinani.com', 'albert.karanja@vetmashinani.com', 'carla.mutindi@vetmashinani.com',
    'miriam.bett@vetmashinani.com', 'william.mwaura@vetmashinani.com', 'amina.jibril@vetmashinani.com',
    'alex.gathu@vetmashinani.com', 'hannah.kiragu@vetmashinani.com', 'felix.waweru@vetmashinani.com',
    'jacob.otieno@vetmashinani.com', 'ruth.mwathi@vetmashinani.com', 'benson.kangethe@vetmashinani.com',
    'margaret.nyambura@vetmashinani.com', 'bernard.mwaura@vetmashinani.com', 'grace.nyambura@vetmashinani.com',
    'douglas.muriithi@vetmashinani.com', 'janet.macharia@vetmashinani.com', 'nelly.mwangi@vetmashinani.com',
    'michael.mbugua@vetmashinani.com', 'racheal.kamau@vetmashinani.com', 'lilian.obara@vetmashinani.com',
    'jack.mutai@vetmashinani.com', 'esther.munyua@vetmashinani.com', 'benjamin.kiplagat@vetmashinani.com',
    'edith.njoroge@vetmashinani.com'
]

# API URL
url = "https://michaelotienokasuku.pythonanywhere.com/signup/"

# Common password
password = "Student1@2023"

# Loop to create users
for i, email in enumerate(vet_emails):
    # Extract username from the email address (before the @ symbol)
    username = email.split('@')[0]
    
    # Randomly pick a county from the list
    county = random.choice(counties)
    
    data = {
        "username": username,
        "email": email,
        "password": password,
        "is_vet": True,
        "is_farmer": False,
        "location_lat": county['lat'],
        "location_lng": county['lng']
    }

    # Send POST request to signup endpoint
    response = requests.post(url, json=data)
    
    # Check if the response is successful
    if response.status_code == 201:
        print(f"Successfully created user with email: {email}")
    else:
        print(f"Failed to create user with email: {email}, Status code: {response.status_code}, Error: {response.text}")

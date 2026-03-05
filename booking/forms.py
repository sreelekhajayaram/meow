from django import forms
from .models import PortraitBooking
from shop.models import Category
import json


INDIAN_STATES = [
    ('', 'Select State'),
    ('Andaman and Nicobar Islands','Andaman and Nicobar Islands'),
    ('Andhra Pradesh','Andhra Pradesh'),
    ('Arunachal Pradesh','Arunachal Pradesh'),
    ('Assam','Assam'),
    ('Bihar','Bihar'),
    ('Chandigarh','Chandigarh'),
    ('Chhattisgarh','Chhattisgarh'),
    ('Dadra and Nagar Haveli and Daman and Diu','Dadra and Nagar Haveli and Daman and Diu'),
    ('Delhi','Delhi'),
    ('Goa','Goa'),
    ('Gujarat','Gujarat'),
    ('Haryana','Haryana'),
    ('Himachal Pradesh','Himachal Pradesh'),
    ('Jammu and Kashmir','Jammu and Kashmir'),
    ('Jharkhand','Jharkhand'),
    ('Karnataka','Karnataka'),
    ('Kerala','Kerala'),
    ('Ladakh','Ladakh'),
    ('Lakshadweep','Lakshadweep'),
    ('Madhya Pradesh','Madhya Pradesh'),
    ('Maharashtra','Maharashtra'),
    ('Manipur','Manipur'),
    ('Meghalaya','Meghalaya'),
    ('Mizoram','Mizoram'),
    ('Nagaland','Nagaland'),
    ('Odisha','Odisha'),
    ('Puducherry','Puducherry'),
    ('Punjab','Punjab'),
    ('Rajasthan','Rajasthan'),
    ('Sikkim','Sikkim'),
    ('Tamil Nadu','Tamil Nadu'),
    ('Telangana','Telangana'),
    ('Tripura','Tripura'),
    ('Uttar Pradesh','Uttar Pradesh'),
    ('Uttarakhand','Uttarakhand'),
    ('West Bengal','West Bengal'),
]

# ============================================================
# FRAME CHOICES - Part 1
# ============================================================
FRAME_CHOICES = [
    ('', 'Select Frame Type'),
    ('Plastic', 'Plastic'),
    ('Wooden', 'Wooden'),
    ('Metal', 'Metal'),
    ('Premium Wooden', 'Premium Wooden'),
    ('Vintage Gold', 'Vintage Gold'),
    ('Matte Black', 'Matte Black'),
]

# ============================================================
# CATEGORY CHOICES - Part 2
# Updated to: Caricature, Pen Art, Painting, Pencil Drawing, Stencil Art
# ============================================================
CATEGORY_CHOICES = [
    ('', 'Select Category'),
    ('caricature', 'Caricature'),
    ('pen_art', 'Pen Art'),
    ('paintings', 'Painting'),
    ('pencil', 'Pencil Drawing'),
    ('stencil', 'Stencil Art'),
]

# State-District Mapping for dynamic dropdown (All Indian Districts)
INDIA_STATE_DISTRICTS = {
    'Andhra Pradesh': [
        "Anakapalli","Anantapur","Annamayya","Bapatla","Chittoor",
        "East Godavari","Eluru","Guntur","Kakinada","Konaseema",
        "Krishna","Kurnool","Nandyal","Nellore","Palnadu",
        "Parvathipuram Manyam","Prakasam","Sri Sathya Sai",
        "Srikakulam","Tirupati","Visakhapatnam","Vizianagaram",
        "West Godavari","YSR Kadapa"
    ],
    'Arunachal Pradesh': [
        "Anjaw","Changlang","Dibang Valley","East Kameng",
        "East Siang","Kamle","Kra Daadi","Kurung Kumey",
        "Lepa Rada","Lohit","Longding","Lower Dibang Valley",
        "Lower Siang","Lower Subansiri","Namsai",
        "Pakke Kessang","Papum Pare","Shi Yomi",
        "Siang","Tawang","Tirap","Upper Siang",
        "Upper Subansiri","West Kameng","West Siang"
    ],
    'Assam': [
        "Baksa","Barpeta","Biswanath","Bongaigaon","Cachar",
        "Charaideo","Chirang","Darrang","Dhemaji","Dhubri",
        "Dibrugarh","Dima Hasao","Goalpara","Golaghat",
        "Hailakandi","Hojai","Jorhat","Kamrup",
        "Kamrup Metropolitan","Karbi Anglong",
        "Karimganj","Kokrajhar","Lakhimpur","Majuli",
        "Morigaon","Nagaon","Nalbari","Sivasagar",
        "Sonitpur","South Salmara-Mankachar",
        "Tinsukia","Udalguri","West Karbi Anglong"
    ],
    'Bihar': [
        "Araria","Arwal","Aurangabad","Banka","Begusarai",
        "Bhagalpur","Bhojpur","Buxar","Darbhanga","East Champaran",
        "Gaya","Gopalganj","Jamui","Jehanabad","Kaimur",
        "Katihar","Khagaria","Kishanganj","Lakhisarai",
        "Madhepura","Madhubani","Munger","Muzaffarpur",
        "Nalanda","Nawada","Patna","Purnia","Rohtas",
        "Saharsa","Samastipur","Saran","Sheikhpura",
        "Sheohar","Sitamarhi","Siwan","Supaul",
        "Vaishali","West Champaran"
    ],
    'Chhattisgarh': [
        "Balod","Baloda Bazar","Balrampur","Bastar",
        "Bemetara","Bijapur","Bilaspur","Dantewada",
        "Dhamtari","Durg","Gariaband","Gaurela-Pendra-Marwahi",
        "Janjgir-Champa","Jashpur","Kabirdham","Kanker",
        "Kondagaon","Korba","Koriya","Mahasamund",
        "Mungeli","Narayanpur","Raigarh","Raipur",
        "Rajnandgaon","Sukma","Surajpur","Surguja"
    ],
    'Goa': [
        "North Goa","South Goa"
    ],
    'Gujarat': [
        "Ahmedabad","Amreli","Anand","Aravalli","Banaskantha",
        "Bharuch","Bhavnagar","Botad","Chhota Udaipur",
        "Dahod","Dang","Devbhoomi Dwarka","Gandhinagar",
        "Gir Somnath","Jamnagar","Junagadh","Kheda",
        "Kutch","Mahisagar","Mehsana","Morbi",
        "Narmada","Navsari","Panchmahal","Patan",
        "Porbandar","Rajkot","Sabarkantha","Surat",
        "Surendranagar","Tapi","Vadodara","Valsad"
    ],
    'Haryana': [
        "Ambala","Bhiwani","Charkhi Dadri","Faridabad",
        "Fatehabad","Gurugram","Hisar","Jhajjar",
        "Jind","Kaithal","Karnal","Kurukshetra",
        "Mahendragarh","Nuh","Palwal","Panchkula",
        "Panipat","Rewari","Rohtak","Sirsa",
        "Sonipat","Yamunanagar"
    ],
    'Himachal Pradesh': [
        "Bilaspur","Chamba","Hamirpur","Kangra",
        "Kinnaur","Kullu","Lahaul and Spiti",
        "Mandi","Shimla","Sirmaur","Solan","Una"
    ],
    'Jharkhand': [
        "Bokaro","Chatra","Deoghar","Dhanbad",
        "Dumka","East Singhbhum","Garhwa","Giridih",
        "Godda","Gumla","Hazaribagh","Jamtara",
        "Khunti","Koderma","Latehar","Lohardaga",
        "Pakur","Palamu","Ramgarh","Ranchi",
        "Sahibganj","Seraikela Kharsawan","Simdega",
        "West Singhbhum"
    ],
    'Karnataka': [
        "Bagalkot","Ballari","Belagavi","Bengaluru Rural",
        "Bengaluru Urban","Bidar","Chamarajanagar",
        "Chikkaballapur","Chikkamagaluru","Chitradurga",
        "Dakshina Kannada","Davanagere","Dharwad",
        "Gadag","Hassan","Haveri","Kalaburagi",
        "Kodagu","Kolar","Koppal","Mandya",
        "Mysuru","Raichur","Ramanagara","Shivamogga",
        "Tumakuru","Udupi","Uttara Kannada",
        "Vijayanagara","Vijayapura","Yadgir"
    ],
    'Kerala': [
        "Alappuzha","Ernakulam","Idukki","Kannur",
        "Kasaragod","Kollam","Kottayam","Kozhikode",
        "Malappuram","Palakkad","Pathanamthitta",
        "Thiruvananthapuram","Thrissur","Wayanad"
    ],
    'Madhya Pradesh': [
        "Agar Malwa","Alirajpur","Anuppur","Ashoknagar",
        "Balaghat","Barwani","Betul","Bhind","Bhopal",
        "Burhanpur","Chhatarpur","Chhindwara","Damoh",
        "Datia","Dewas","Dhar","Dindori","Guna",
        "Gwalior","Harda","Hoshangabad","Indore",
        "Jabalpur","Jhabua","Katni","Khandwa",
        "Khargone","Mandla","Mandsaur","Morena",
        "Narsinghpur","Neemuch","Panna","Raisen",
        "Rajgarh","Ratlam","Rewa","Sagar","Satna",
        "Sehore","Seoni","Shahdol","Shajapur",
        "Sheopur","Shivpuri","Sidhi","Singrauli",
        "Tikamgarh","Ujjain","Umaria","Vidisha"
    ],
    'Maharashtra': [
        "Ahmednagar","Akola","Amravati","Aurangabad","Beed",
        "Bhandara","Buldhana","Chandrapur","Dhule","Gadchiroli",
        "Gondia","Hingoli","Jalgaon","Jalna","Kolhapur",
        "Latur","Mumbai City","Mumbai Suburban","Nagpur",
        "Nanded","Nandurbar","Nashik","Osmanabad","Palghar",
        "Parbhani","Pune","Raigad","Ratnagiri","Sangli",
        "Satara","Sindhudurg","Solapur","Thane","Wardha",
        "Washim","Yavatmal"
    ],
    'Manipur': [
        "Bishnupur","Chandel","Churachandpur","Imphal East",
        "Imphal West","Jiribam","Kakching","Kamjong",
        "Kangpokpi","Noney","Pherzawl","Senapati",
        "Tamenglong","Tengnoupal","Thoubal","Ukhrul"
    ],
    'Meghalaya': [
        "East Garo Hills","East Jaintia Hills","East Khasi Hills",
        "North Garo Hills","Ri Bhoi","South Garo Hills",
        "South West Garo Hills","South West Khasi Hills",
        "West Garo Hills","West Jaintia Hills","West Khasi Hills"
    ],
    'Mizoram': [
        "Aizawl","Champhai","Hnahthial","Khawzawl",
        "Kolasib","Lawngtlai","Lunglei","Mamit",
        "Saiha","Saitual","Serchhip"
    ],
    'Nagaland': [
        "Chumoukedima","Dimapur","Kiphire","Kohima",
        "Longleng","Mokokchung","Mon","Niuland",
        "Noklak","Peren","Phek","Shamator",
        "Tseminyu","Tuensang","Wokha","Zunheboto"
    ],
    'Odisha': [
        "Angul","Balangir","Balasore","Bargarh",
        "Bhadrak","Boudh","Cuttack","Deogarh",
        "Dhenkanal","Gajapati","Ganjam","Jagatsinghpur",
        "Jajpur","Jharsuguda","Kalahandi","Kandhamal",
        "Kendrapara","Kendujhar","Khordha","Koraput",
        "Malkangiri","Mayurbhanj","Nabarangpur","Nayagarh",
        "Nuapada","Puri","Rayagada","Sambalpur",
        "Subarnapur","Sundargarh"
    ],
    'Punjab': [
        "Amritsar","Barnala","Bathinda","Faridkot",
        "Fatehgarh Sahib","Fazilka","Ferozepur","Gurdaspur",
        "Hoshiarpur","Jalandhar","Kapurthala","Ludhiana",
        "Malerkotla","Mansa","Moga","Mohali",
        "Muktsar","Nawanshahr","Pathankot","Patiala",
        "Rupnagar","Sangrur","Tarn Taran"
    ],
    'Rajasthan': [
        "Ajmer","Alwar","Anupgarh","Balotra",
        "Banswara","Baran","Barmer","Beawar",
        "Bharatpur","Bhilwara","Bikaner","Bundi",
        "Chittorgarh","Churu","Dausa","Deeg",
        "Dholpur","Didwana-Kuchaman","Dudu","Dungarpur",
        "Ganganagar","Gangapur City","Hanumangarh",
        "Jaipur","Jaipur Rural","Jaisalmer","Jalore",
        "Jhalawar","Jhunjhunu","Jodhpur","Jodhpur Rural",
        "Karauli","Kekri","Khairthal-Tijara","Kota",
        "Kotputli-Behror","Nagaur","Neem Ka Thana",
        "Pali","Phalodi","Pratapgarh","Rajsamand",
        "Salumbar","Sanchore","Sawai Madhopur",
        "Shahpura","Sikar","Sirohi","Tonk","Udaipur"
    ],
    'Sikkim': [
        "Gangtok","Gyalshing","Mangan","Namchi","Pakyong","Soreng"
    ],
    'Tamil Nadu': [
        "Ariyalur","Chengalpattu","Chennai","Coimbatore",
        "Cuddalore","Dharmapuri","Dindigul","Erode",
        "Kallakurichi","Kancheepuram","Karur","Krishnagiri",
        "Madurai","Mayiladuthurai","Nagapattinam","Namakkal",
        "Nilgiris","Perambalur","Pudukkottai","Ramanathapuram",
        "Ranipet","Salem","Sivaganga","Tenkasi",
        "Thanjavur","Theni","Thoothukudi","Tiruchirappalli",
        "Tirunelveli","Tirupathur","Tiruppur","Tiruvallur",
        "Tiruvannamalai","Tiruvarur","Vellore",
        "Viluppuram","Virudhunagar"
    ],
    'Telangana': [
        "Adilabad","Bhadradri Kothagudem","Hanamkonda",
        "Hyderabad","Jagtial","Jangaon","Jayashankar Bhupalpally",
        "Jogulamba Gadwal","Kamareddy","Karimnagar",
        "Khammam","Komaram Bheem","Mahabubabad",
        "Mahabubnagar","Mancherial","Medak",
        "Medchal–Malkajgiri","Mulugu","Nagarkurnool",
        "Nalgonda","Narayanpet","Nirmal","Nizamabad",
        "Peddapalli","Rajanna Sircilla","Rangareddy",
        "Sangareddy","Siddipet","Suryapet",
        "Vikarabad","Wanaparthy","Warangal","Yadadri Bhuvanagiri"
    ],
    'Tripura': [
        "Dhalai","Gomati","Khowai","North Tripura",
        "Sepahijala","South Tripura","Unakoti","West Tripura"
    ],
    'Uttar Pradesh': [
        "Agra","Aligarh","Ambedkar Nagar","Amethi","Amroha",
        "Auraiya","Ayodhya","Azamgarh","Baghpat","Bahraich",
        "Ballia","Balrampur","Banda","Barabanki","Bareilly",
        "Basti","Bhadohi","Bijnor","Budaun","Bulandshahr",
        "Chandauli","Chitrakoot","Deoria","Etah","Etawah",
        "Farrukhabad","Fatehpur","Firozabad","Gautam Buddha Nagar",
        "Ghaziabad","Ghazipur","Gonda","Gorakhpur","Hamirpur",
        "Hapur","Hardoi","Hathras","Jalaun","Jaunpur",
        "Jhansi","Kannauj","Kanpur Dehat","Kanpur Nagar",
        "Kasganj","Kaushambi","Kheri","Kushinagar","Lalitpur",
        "Lucknow","Maharajganj","Mahoba","Mainpuri","Mathura",
        "Mau","Meerut","Mirzapur","Moradabad","Muzaffarnagar",
        "Pilibhit","Pratapgarh","Prayagraj","Raebareli",
        "Rampur","Saharanpur","Sambhal","Sant Kabir Nagar",
        "Shahjahanpur","Shamli","Shrawasti","Siddharthnagar",
        "Sitapur","Sonbhadra","Sultanpur","Unnao","Varanasi"
    ],
    'Uttarakhand': [
        "Almora","Bageshwar","Chamoli","Champawat",
        "Dehradun","Haridwar","Nainital",
        "Pauri Garhwal","Pithoragarh","Rudraprayag",
        "Tehri Garhwal","Udham Singh Nagar","UTTARKASHI"
    ],
    'West Bengal': [
        "Alipurduar","Bankura","Birbhum","Cooch Behar",
        "Dakshin Dinajpur","Darjeeling","Hooghly","Howrah",
        "Jalpaiguri","Jhargram","Kalimpong","Kolkata",
        "Malda","Murshidabad","Nadia","North 24 Parganas",
        "Paschim Bardhaman","Paschim Medinipur",
        "Purba Bardhaman","Purba Medinipur",
        "Purulia","South 24 Parganas","Uttar Dinajpur"
    ],
    # Union Territories and other states
    'Andaman and Nicobar Islands': ['Port Blair', 'Car Nicobar', 'Great Nicobar', 'Middle Andaman', 'South Andaman'],
    'Chandigarh': ['Chandigarh'],
    'Dadra and Nagar Haveli and Daman and Diu': ['Silvassa', 'Daman', 'Diu', 'Dadra', 'Nagar Haveli'],
    'Delhi': ['New Delhi', 'Central Delhi', 'East Delhi', 'New Delhi', 'North Delhi', 'North East Delhi', 'North West Delhi', 'Shahdara', 'South Delhi', 'South East Delhi', 'South West Delhi', 'West Delhi'],
    'Jammu and Kashmir': ['Srinagar', 'Jammu', 'Leh', 'Kashmir', 'Jammu', 'Kargil', 'Poonch', 'Rajouri', 'Kathua', 'Udhampur'],
    'Ladakh': ['Leh', 'Kargil'],
    'Lakshadweep': ['Kavaratti', 'Agatti', 'Minicoy', 'Andrott', 'Kalpeni', 'Kadamath'],
    'Puducherry': ['Puducherry', 'Yanam', 'Karaikal', 'Mahe'],
}

SIZE_CHOICES_WITH_DESC = [
    ('8x10', '8" × 10"'),
    ('A4', '8.3" × 11.7" (A4)'),
    ('11x14', '11" × 14"'),
    ('A3', '11.7" × 16.5" (A3)'),
    ('16x20', '16" × 20"'),
    ('A2', '16.5" × 23.4" (A2)'),
]

SIZE_DESCRIPTIONS = {
    '8x10': {
        'title': '8" × 10"',
        'description': 'Small, detailed portrait or single subject artwork. Best for close-up facial studies.',
        'ideal': '✓ Best for: Single portrait, face close-up | Perfect for: Desk, shelf, small wall'
    },
    'A4': {
        'title': '8.3" × 11.7" (A4)',
        'description': 'Single head-and-shoulders portrait with balanced composition. Ideal for quick commissions.',
        'ideal': '✓ Best for: Portrait paintings, pencil drawings | Perfect for: Compact spaces, desks'
    },
    '11x14': {
        'title': '11" × 14"',
        'description': 'Single or couple portraits with shoulder-to-torso view. Great detail and presence.',
        'ideal': '✓ Best for: Paintings, stencil art, couple portraits | Perfect for: Bedroom, living room'
    },
    'A3': {
        'title': '11.7" × 16.5" (A3)',
        'description': 'Couple or two-figure portraits with rich detail. Excellent for detailed stencil artwork.',
        'ideal': '✓ Best for: Detailed paintings, stencil art, couple compositions | Perfect for: Gallery walls'
    },
    '16x20': {
        'title': '16" × 20"',
        'description': 'Statement artwork or family portraits (up to 3 people). Maximum detail and impact.',
        'ideal': '✓ Best for: Family portraits, large paintings, caricatures | Perfect for: Living room focal point'
    },
    'A2': {
        'title': '16.5" × 23.4" (A2)',
        'description': 'Large premium artwork with exceptional visual presence. Perfect for showcase pieces.',
        'ideal': '✓ Best for: Premium paintings, group portraits, exhibition art | Perfect for: Statement wall'
    },
}


class PortraitBookingForm(forms.ModelForm):
    total_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label='Total Price (₹)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'id': 'totalPriceInput',
            'readonly': True,
            'placeholder': 'Calculated automatically'
        })
    )

    class Meta:
        model = PortraitBooking
        # ============================================================
        # ADDED 'frame_type' - Part 1
        # ============================================================
        fields = [
            'name', 'email', 'phone',
            'address', 'state', 'district', 'pincode',
            'category', 'size', 'frame_type', 'reference_image', 'description', 'price'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Your full name',
                'autocomplete': 'name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'you@example.com',
                'autocomplete': 'email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '+91 XXXXX XXXXX',
                'autocomplete': 'tel'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control form-control-lg',
                'placeholder': 'Describe your vision for the artwork...'
            }),
            'address': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control form-control-lg',
                'placeholder': 'Street address',
                'autocomplete': 'address-line1'
            }),
            'district': forms.Select(attrs={
                'class': 'form-control form-control-lg',
                'id': 'districtSelect',
                'autocomplete': 'address-level2'
            }),
            'state': forms.Select(
                choices=INDIAN_STATES,
                attrs={
                    'class': 'form-control form-control-lg',
                    'id': 'stateSelect',
                    'autocomplete': 'address-level1'
                }
            ),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'PIN code',
                'pattern': '[0-9]{6}',
                'maxlength': '6',
                'autocomplete': 'postal-code'
            }),
            'reference_image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
            'size': forms.Select(
                choices=SIZE_CHOICES_WITH_DESC,
                attrs={
                    'class': 'form-control form-control-lg',
                    'id': 'sizeSelect'
                }
            ),
            # ============================================================
            # NEW: Frame type dropdown widget - Part 1
            # ============================================================
            'frame_type': forms.Select(
                choices=FRAME_CHOICES,
                attrs={
                    'class': 'form-control form-control-lg',
                    'id': 'frameTypeSelect'
                }
            ),
            'price': forms.HiddenInput(attrs={'id': 'priceInput'}),
            'total_price': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'id': 'totalPriceInput',
                'readonly': True,
                'placeholder': 'Calculated automatically'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Update district field to be a select with dynamic options
        all_districts = [('', 'Select District')]
        for districts in INDIA_STATE_DISTRICTS.values():
            for district in districts:
                if (district, district) not in all_districts:
                    all_districts.append((district, district))

        self.fields['district'] = forms.ChoiceField(
            choices=all_districts,
            widget=forms.Select(attrs={
                'class': 'form-control form-control-lg',
                'id': 'districtSelect'
            }),
            required=True
        )

        # ============================================================
        # UPDATED Category field - Part 2
        # Using fixed CATEGORY_CHOICES instead of dynamic from model
        # ============================================================
        self.fields['category'] = forms.ChoiceField(
            choices=CATEGORY_CHOICES,
            widget=forms.Select(attrs={
                'class': 'form-control form-control-lg',
                'id': 'categorySelect'
            }),
            required=True
        )

        # Make email read-only and populate from user
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['class'] = 'form-control form-control-lg bg-light'

        # Make reference_image required
        self.fields['reference_image'].required = True

        # Add labels with proper formatting
        self.fields['name'].label = 'Full Name'
        self.fields['email'].label = 'Email Address'
        self.fields['phone'].label = 'Phone Number'
        self.fields['address'].label = 'Street Address'
        self.fields['state'].label = 'State'
        self.fields['district'].label = 'District'
        self.fields['pincode'].label = 'PIN Code'
        self.fields['reference_image'].label = 'Upload Reference Image'
        self.fields['size'].label = 'Artwork Size'
        # ============================================================
        # UPDATED: Category label - Part 2
        # ============================================================
        self.fields['category'].label = 'Artwork Category'
        # ============================================================
        # NEW: Frame type label - Part 1
        # ============================================================
        self.fields['frame_type'].label = 'Select Frame Type'
        self.fields['description'].label = 'Additional Details'
        self.fields['total_price'].label = 'Total Price (₹)'

        # Add help text
        self.fields['pincode'].help_text = '6-digit postal code'
        self.fields['reference_image'].help_text = 'Upload a clear reference image (JPG, PNG)'
        # ============================================================
        # NEW: Frame type help text - Part 1
        # ============================================================
        self.fields['frame_type'].help_text = 'Choose your preferred frame type'

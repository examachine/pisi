component'larla ilgili notlar

1. Temel feature'lar (Eray)
--------------------

Iki yerde component tag'i tanimladik simdiye kadar, bir
source'larda bir de binary'lerde. Binary'de tanimlanan component default 
olarak source'daki tanimi inherit ediyor ve tanimlanan component'i override 
edebiliyor.

Bir component temel olarak bir meta-package, icerisinde paketler olan
bir paket. Bir component'in icerisinde bir takim source'lar ve bir takim
binary'ler bulunuyor diye bakabiliriz. Sanirim query'leri bu sekilde yapmak 
mumkun olmali.

$ pisi list-components
$ pisi info system.base
  Source packages in system.base:
    ....
    ....
  Binary packages in system.base:
    ....
    ....

gibi ozellikler eklemeyi umit ediyorum.

Source'larin component tag'leri de, gene sadece bir senaryo konusuyorum,
direkt olarak directory structure'indan inherit alinacak. Ayni zamanda o pspec 
icin de bir tane component tanimlananack default olarak, ve bu component o 
scope'da tanimlanmis olan butun binary package'lari icerecek. 

Ornegin diyelim ki a/b/c/pspec.xml var ve c1 c2 c3 seklinde uc tane paket 
tanimliyor. Hic bir component tanimi yapilmadigi zaman otomatik olarak bir
a.b.c component'i olusturulacak, ve bu component'in icerisinde c1 c2 c3 
bulunacak. 

$ pisi info a.b.c
  Source packages:
    c  - oldur beni yarim sen olmazsan biterim
  Binary packages:
    c1 - bu aksam demlenmemek sonum olur benim
    c2 - sincaplarla konustum butun gece
    c3 - her gul gordugumde icim kan aglar

Bu varsayilan davranis, ama  bunu degistirmek mumkun olacak. Burada yamuk 
gozukebilecek bir sey var, o da tek bir paket oldugunda sanki biraz 
redundancy olmasi, o takdirde bir optimizasyon olarak, diyelim ki 
a/b/c/pspec.xml'in icerisinde tek bir paket tanimli c1

$ pisi info a.b
   ....
   c1 - dil dil dillerdeyim

olabilir bu durumda, bu genel agac mantiginda bir sorun yaratmayacaktir.


2. Temel tanım (Barış)

fiziksel aitlik: kdebase'den çıkan kcontrol gibi; grup aitliği: pdf 
göstericileri gibi...


3. Database XML ayrımı (Barış)

Component database'i ile component.xml ayrı olmalı. Component database, 
pisi'nin pisi-index.xml dosyasını okuyarak oluşturacağı bir veritabanı. Hangi 
paketler hangi componentlere dahil, vs. sorguları bu veritabanından 
yapılacak.

Pspec dosyasını hatırlayalım. İçerisinde bir <PartOf> diye bir tag var. 
Oluşturulacak paketin hangi component'e ait olduğunu belirtiyor. Bu bilgi 
pisi-index.xml dosyasına da koyulmalı.

4. PL modüllerine benzerlik (Eray)

component tag'leri Java ya da python'daki gibi
directory yapisindan cikiyor. Yani pisi bir programlama dili olsaydi 
component'lar module'ler ya da package'larla es anlamli olacakti.

5. Mereology ve Eray'ın açıklama çabaları (Eray)

PartOf iliskisi hakkında su kadarini soylemek yeter: eger a b'nin bir parcasiysa, 
a'nin fonksiyonu b'nin fonksiyonunun bir parcasidir. Bu da fiziksel sistemler 
icin bir principle of compositionality'nin varligindan hareket eder [*]

Genel olarak da software engineering ve AI camiasinda module'un tanimi gayet 
iyi bilinir. Bir modul icerisindeki bagimliliklar yogundur. Moduller arasindaki 
bagimliliklar zayiftir. 

Bu tanim sadece software engineering'de degil, nesneler arasindaki 
benzerliklerin incelendigi bir cok disiplinde kullanilan informal bir tanim, 
ama tabii ki formule dokulmus bir ton hali var.Sırf bu tanımı taban alarak 
yazılmış başarılı kümeleme (clustering) algoritmaları var.

Modulerlik tanimi verilen *fiziksel* modul ve parcasi olma iliskisiyle 
birlesince birlikte install edilip remove edilme yahut ortak bağımlılıklara
sahip olma tanımlarına götürür.

Bu tanımı analiz edebilmek için parcasi olma iliskisininin anlamini 
korumamiz yeterli. Temel olarak

  kol insanin parcasidir

iliskisi burada yer aliyor.  Eger

  a partof b 

turu iliskilerde a paket ya da component, ve b component ise, a ve b'nin
iliskisinin kol ve insan iliskisi gibi olmasini bekleriz. Eger bu parca-butun 
iliskisini ihlal ediyorsa o zaman muhtemelen yanlis bir iliski bulunmus 
demektir. 

Bunun turlu sonuclari da onem sirasina gore soyle dizilebilir:

1. Fonksiyonlarin bolunebilmesi prensibinden: (basit bir sonuç)
   a's function is part-of b's function

   orneğin kolun fonksiyonu insanın total fonksiyonunun bir parçasıdır.

paket ornegi: pisi'nin fonksiyonu olan paket yükleme/çıkarma system.base'in fonksiyonunun, yani temel pardus sisteminin fonksiyonunun bir parçasıdır.

2. Karmasik sistemlerde birbirine dayanan ufak parcalarin kararli yapilar 
meydana getirmesi prensibinden: (evrimsel sonuç)

   if a is a part-of c, and b is a part-of c, then it follows that a and b 
may:
     a. have many interdependencies
     b. share in their origins
  (which are about the same thing)

2b. sonucunun bizim durumumuza uygulanması, source code'un aynı kaynaktan
çıkması, birlikte inşa edilmeleri gibi şartları getirir. Bunun oldukça
olasi, en azindan insa metodlarinin ve kaynaklarının birbirine benzemesini 
bekleriz. Yalniz, 2.a'daki bagimliliklar sadece insa ile degil ayni zamanda 
calisma ile de alakalidir. Kaynakları farklı parçaların birbirine bağımlı
hale gelebilecegini unutmamak gerekir.

Fedora'nin yaklasiminin hos tarafi, boyle teknik ayrintilara girmeden "package 
group" mantigini kullanmasiydi, ama bizim belli bir anlami olan parca-butun 
iliskisini korumamiz daha mantikli bir yazilim ontology'si ortaya 
cikaracaktir. Onlarin yaklasimi ise "anything goes", grup ile kategori'nin 
temel bir farki yok cunku, herhangi bir bakis acisi olabilir "grup".


6. Modulleri test etmek (!!) (Eray)
------------------------------------

PISI'deki seçilen implementation detaylari bir tanima cok fazla commitment 
yapmiyor, implementation'ın getirdiği tek şey paketleri bir ağaca koymak.
Component'ların seçiminin ne kadar kaliteli olduğunu belirleyemiyor. 
Paketlerin ve componentlarin secimi yapiyor, ki kritik olan o. 
Yalnız modulerlik tanimindan ve part-of iliskisinin 
  if a is part of b, and b is part of c, then a is part of c.
  if a is part of b, and b is not part of c, then a is not part of c.
gibi sonuclari getirmesinden hareketle (ki bunlar klasik computational 
ontology) kismen test edebilecegimiz bir sekil aliyor ornegin bagimlilik 
graph'ini cluster ederek, ya da her modul icin bir modulerlik sayisi 
hesaplayarak. Daha az formal olarak da bu sonuçları kafamızda yürüterek
yaptığımız componentların ne kadar akla yatkın olduğunu bulabiliriz.


7. Cagların frugalware önerisi
------------------------------

http://ftp.frugalware.org/pub/frugalware/frugalware-current/source/ 
adresindeki yerleşimin hem source hem de binary depo için uygulanmasını ve 
kategori, componentların da bundan çıkartılmasını öneriyorum.

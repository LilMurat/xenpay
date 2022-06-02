"""
    xenpay: Arduino ile RFID yerel ödeme sistemi

    Copyright (C) 2022 Murat Coşkun

    Bu program özgür yazılımdır: Özgür Yazılım Vakfı tarafından yayımlanan GNU Genel Kamu Lisansı’nın sürüm 3 ya da (isteğinize bağlı olarak) daha sonraki sürümlerinin hükümleri altında yeniden dağıtabilir ve/veya değiştirebilirsiniz.

    Bu program, yararlı olması umuduyla dağıtılmış olup, programın BİR TEMİNATI YOKTUR; TİCARETİNİN YAPILABİLİRLİĞİNE VE ÖZEL BİR AMAÇ İÇİN UYGUNLUĞUNA dair bir teminat da vermez. Ayrıntılar için GNU Genel Kamu Lisansı’na göz atınız.

    Bu programla birlikte GNU Genel Kamu Lisansı’nın bir kopyasını elde etmiş olmanız gerekir. Eğer elinize ulaşmadıysa <http://www.gnu.org/licenses/> adresine bakınız.
"""

from datetime import datetime
import os
import sys
import serial
import time
from datetime import datetime

portadı = "/dev/ttyACM0"
baudrate = 9600
eskipwd = ""
günlükm = ""


class VeriTabanı:
    def __init__(self):
        if not os.system("ls veritabanı > /dev/null 2>&1") == 0:
            os.system("mkdir veritabanı")
    def bakiye(self, kartkimlik):
        if not os.system("ls veritabanı/" + str(kartkimlik) + "/ > /dev/null 2>&1") == 0:
           os.system("mkdir veritabanı/" + str(kartkimlik) + "/")
           os.system("echo 0 > veritabanı/" + str(kartkimlik) + "/bakiye")
           return 0;
        else:
            return float(open("veritabanı/" + str(kartkimlik) + "/bakiye", "r").read())
    def bakiye_yaz(self, kartkimlik, bakiye):
        if not os.system("ls veritabanı/" + str(kartkimlik) + "/ > /dev/null 2>&1") == 0:
            os.system("mkdir veritabanı/" + str(kartkimlik) + "/")
            os.system("tocuh veritabanı/" + str(kartkimlik) + "/bakiye")
        os.system("echo " + str(bakiye) + " > veritabanı/" + str(kartkimlik) + "/bakiye")
    def kartbloke(self, kartkimlik, bloke):
        if not bloke == 0 and not bloke == 1: return
        if not os.system("ls veritabanı/" + str(kartkimlik) + "/ > /dev/null 2>&1") == 0:
            os.system("mkdir veritabanı/" + str(kartkimlik) + "/")
            os.system("touch veritabanı/" + str(kartkimlik) + "/bloke")
        os.system("echo " + str(bloke) + " > veritabanı/" + str(kartkimlik) + "/bloke")
    def kartbloke_oku(self, kartkimlik):
        if not os.system("ls veritabanı/" + str(kartkimlik) + "/ > /dev/null 2>&1") == 0:
            os.system("mkdir veritabanı/" + str(kartkimlik) + "/")
            os.system("echo 0 > veritabanı/" + str(kartkimlik) + "/bloke")
        return int(open("veritabanı/" + str(kartkimlik) + "/bloke", "r").read())
    def kart_sil(self, kartkimlik):
        os.system("rm -rf veritabanı/" + str(kartkimlik) + "/")
    def kart_oluştur(self, kartkimlik):
        if os.system("ls veritabanı/" + str(kartkimlik) + "/ > /dev/null 2>&1") == 0:
            os.system("mkdir veritabanı/" + str(kartkimlik) + "/")
            os.system("echo 0 > veritabanı/" + str(kartkimlik) + "/bakiye")
            os.system("echo 0 > veritabanı/" + str(kartkimlik) + "/bloke")
    def kart_sıfırla(self, kartkimlik):
        if not os.system("ls veritabanı/" + str(kartkimlik) + "/ > /dev/null 2>&1") == 0: return
        os.system("echo 0 > veritabanı/" + str(kartkimlik) + "/bakiye")
        os.system("echo 0 > veritabanı/" + str(kartkimlik) + "/bloke")
    def veritabanı_sıfırla(self):
        os.system("rm -rf veritabanı/*")
    def veritabanı_sil(self):
        os.system("rm -rf veritabanı")

        
vt = VeriTabanı()

def günlük(mesaj):
    global günlükm
    günlükm += "(" + datetime.now().strftime("%H:%M:%S") + ")" + mesaj + "\n"

def çıkış(kod):
    günlük("[i]  çıkış yapıldı -> " + str(kod))
    if os.system("ls günlük.log > /dev/null 2>&1") == 0:
        os.system("rm günlük.log")
    d = open("günlük.log", "a")
    d.write(günlükm)
    d.close()
    sys.exit(kod)

def kabuk():
    günlük("[i]  " + portadı + " portuna bağlantı sağlandı")
    günlük("[i]  kabuğa giriş yapıldı")
    print("\nKabuk ortamına hoş geldiniz. Komutların bir listesi için \"yardım\", çıkmak için \"çıkış\" komutunu kullanın.\n\n")
    while True:
        try: komut = str(input("xendpayd> "))
        except: çıkış(0)
        if komut == "çıkış":
            çıkış(0)
        
        if komut == "yardım":
            print("""
            çıkış                                        ::  çıkış yapar
            yardım                                       ::  komutların bir listesini gösterir
            ödeme                                        ::  yeni bir ödeme işlemi başlatır
            günlük                                       ::  günlük kayıtlarını gösterir
            bakiye                                       ::  kartın kimliğine göre bakiyesini sorgular
            bakiyeyaz                                    ::  kartın kimliğine göre bakiyeyi değiştirir
            bakiyeekle                                   ::  kartın kimliğine göre belirtilen miktarda bakiye ekler
            bakiyeçıkar                                  ::  kartın kimliğine göre belirtilen miktarda bakiye çıkarır
            bloke                                        ::  kartın kimliğine göre bloke durumunu değiştirir 
            blokekontrol                                 ::  kartın kimliğine göre bloke durumunu sorgular
            kartoluştur                                  ::  belirtilen kimliğe sahip kart oluşturur
            kartsil                                      ::  belirtilen kimliğe sahip kartı siler
            kartsıfırla                                  ::  belirtilen kimliğe sahip kartı sıfırlar
            veritabanısıfırla                            ::  veritabanını sıfırlar
            veritabanısil                                ::  veritabanını siler
            """)
        
        if komut == "ödeme":
            miktar = float(input("Ödeme miktarı: "))
            print("Lütfen kartı okuyucuya okutun...")
            kimlik = port.readline()
            if kimlik == None: print("işlem iptal edildi.")
            else:
                kartkimlik = "xencard-" + str(len(kimlik) * len(sys.platform) * 6783409 + baudrate)
                if not os.system("ls veritabanı/" + str(kartkimlik) + "/bloke > /dev/null 2>&1") == 0:
                    os.system("echo 0 > veritabanı/" + str(kartkimlik) + "/bloke")
                işlemkimlik = "xentransaction-" + str(time.time() * os.getpid() + len(kartkimlik) - miktar)
                if vt.kartbloke_oku(kartkimlik) == 1:
                    print("HATA: kart kullanıma kapalı.")
                    günlük("[e]  " + işlemkimlik + " işlemi gerçekleştirilemedi (" + kartkimlik + ") kartı bloke)")
                else:
                    if vt.bakiye(kartkimlik) < miktar:
                        print("HATA: yetersiz bakiye.")
                    else:
                        vt.bakiye_yaz(kartkimlik, vt.bakiye(kartkimlik) - miktar)
                        işlemtarih = datetime.now().strftime("%d.%m.%Y %H:%M:%S (" + str(time.time()) + ")")
                        print("""
== DEKONT ==
                        
                        
İşlem kimliği: %s
Tarih: %s
Miktar: %s 
Kart kimliği: %s
                    
""" % (işlemkimlik, işlemtarih, miktar, kartkimlik))
                        günlük("[i]  " + işlemkimlik + " işlemi gerçekleştirildi [miktar: " + str(miktar) + "] [kart: " + kartkimlik + "]")
        
        if komut == "günlük":
            print(günlükm)
        if komut == "bakiye":
            kimlik = input("Kart kimliği: ")
            print(str(vt.bakiye(kimlik)))
        if komut == "bakiyeyaz":    
            kimlik = input("Kart kimliği: ")
            miktar = float(input("Miktar: "))
            vt.bakiye_yaz(kimlik, miktar)
            print("bakiye -> " + str(vt.bakiye(kimlik)))
            günlük("[i]  " + kimlik + " kartına " + str(miktar) + " bakiye yazıldı")
        if komut == "bakiyeekle":
            kimlik = input("Kart kimliği: ")
            miktar = float(input("Miktar: "))
            vt.bakiye_yaz(kimlik, miktar + vt.bakiye(kimlik))
            print("bakiye -> " + str(vt.bakiye(kimlik)))
            günlük("[i]  " + kimlik + " kartına " + str(miktar) + " bakiye eklendi")
        if komut == "bakiyeçıkar":
            kimlik = input("Kart kimliği: ")
            miktar = float(input("Miktar: "))
            vt.bakiye_yaz(kimlik, vt.bakiye(kimlik) - miktar)
            print("bakiye -> " + str(vt.bakiye(kimlik)))
            günlük("[i]  " + kimlik + " kartından " + str(miktar) + " bakiye eksiltildi")
        if komut == "bloke":
            kimlik = input("Kart kimliği: ")
            bloke = int(input("Bloke durumu (0-1): "))
            vt.kartbloke(kimlik, bloke)
            print("bloke -> " + str(vt.kartbloke_oku(kimlik)))
            günlük("[i]  " + kimlik + " kartının bloke durumu " + str(bloke) + " olarak değiştirildi")
        if komut == "blokekontrol":
            kimlik = input("Kart kimliği: ")
            print(vt.kartbloke_oku(kimlik))
        if komut == "kartoluştur":
            kimlik = input("Kart kimliği: ")
            vt.kart_oluştur(kimlik)
            günlük("[i]  " + kimlik + " kartı oluşturuldu")
        if komut == "kartsil":
            kimlik = input("Kart kimliği: ")
            vt.kart_sil(kimlik)
            günlük("[i]  " + kimlik + " kartı silindi")
        if komut == "kartsıfırla":
            kimlik = input("Kart kimliği: ")
            vt.kart_sıfırla(kimlik)
            günlük("[i]  " + kimlik + " kartı sıfırlandı")
        if komut == "veritabanısıfırla":
            vt.veritabanı_sıfırla()
            günlük("[i]  veritabanı sıfırlandı")
        if komut == "veritabanısil":
            vt.veritabanı_sil()
            günlük("[i]  veritabanı silindi")
        if komut == "çıkış":
            port.close()
            çıkış(0)
        
                
            

def main():
    global port
    portadı = input("Port adı (genellikle COM3 veya /dev/ttyACM0): ")
    günlük("[i]  " + portadı + " portuna bağlanılıyor")
    try: port = serial.Serial(portadı, baudrate)
    except:
        print("\nHATA: port erişimi reddedildi, port adını ve izinlerini kontrol edin.")
        günlük("[e]  " + portadı + " portuna erişilemedi")
        çıkış(1)
    kabuk()

main()
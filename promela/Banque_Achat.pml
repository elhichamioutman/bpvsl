#define Transition 19
int T[Transition];
#define Debut T[0]
#define Demande_achat T[1]
#define Controler_conformite_demande_achat T[2]
#define Achat_conventionne_inferieur_50000Dhs T[3]
#define Rejet_demande_achat T[4]
#define Etablir_demande_cotation T[5]
#define Ou1 T[6]
#define Ou2 T[7]
#define Devis_choisi T[8]
#define Etablir_bon_commande T[9]
#define Fin T[10]
#define Signer_bon_commande T[11]
#define Transmettre_bon_commande_signe T[12]
#define Controler_conformite_comande_bon_livraison T[13]
#define Et1 T[14]
#define Controler_conformite_facture T[15]
#define Archiver_dossier_achat_realise T[16]
#define Regler_facture T[17]
#define Et2 T[18]
#define remove1(x)	(x>0)		-> x--
#define add1(x1)	x1++;
#define add2(x1,x2)	x1++;x2++;
init
{
T[0]=1;
do
:: atomic{remove1(T[0]) -> add1(T[1]);}
:: atomic{remove1(T[1]) -> add1(T[2]);}
:: atomic{remove1(T[2]) -> add1(T[3]);}
:: atomic{remove1(T[2]) -> add1(T[4]);}
:: atomic{remove1(T[3]) -> add1(T[5]);}
:: atomic{remove1(T[3]) -> add1(T[6]);}
:: atomic{remove1(T[4]) -> add1(T[7]);}
:: atomic{remove1(T[5]) -> add1(T[8]);}
:: atomic{remove1(T[6]) -> add1(T[9]);}
:: atomic{remove1(T[7]) -> add1(T[10]);}
:: atomic{remove1(T[8]) -> add1(T[6]);}
:: atomic{remove1(T[9]) -> add1(T[11]);}
:: atomic{remove1(T[11]) -> add1(T[12]);}
:: atomic{remove1(T[12]) -> add1(T[13]);}
:: atomic{remove1(T[13]) -> add1(T[14]);}
:: atomic{remove1(T[14]) -> add2(T[15],T[16]);}
:: atomic{remove1(T[15]) -> add1(T[17]);}
:: atomic{remove1(T[16]) -> add1(T[18]);}
:: atomic{remove1(T[17]) -> add1(T[18]);}
:: atomic{remove1(T[18]) -> add1(T[7]);}
:: else -> skip;
od
}
ltl f0	{<>(Debut>=1)}
ltl f1	{[](Rejet_demande_achat>=1 -> <> (Regler_facture >=1))}
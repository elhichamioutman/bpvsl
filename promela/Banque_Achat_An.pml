#define Transition 19
int T[Transition];
#define Start T[0]
#define Purchase_request T[1]
#define Check_conformity_purchase_request T[2]
#define Purchase_agreement or_less_50000Dhs T[3]
#define Rejection_purchase_requisition T[4]
#define Or1 T[5]
#define Establish_request_quotation T[6]
#define Or2 T[7]
#define Establish_purchase_order T[8]
#define Selected_quote T[9]
#define End T[10]
#define Sign_purchase_order T[11]
#define Transmit_signed_purchase_order T[12]
#define Check_conformity_order_delivery_note T[13]
#define And1 T[14]
#define Check_conformity_invoice T[15]
#define Archive_file_purchase_made T[16]
#define Pay_bill T[17]
#define And2 T[18]
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
:: atomic{remove1(T[8]) -> add1(T[11]);}
:: atomic{remove1(T[9]) -> add1(T[5]);}
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
ltl f0	{<>(Start>=1)}
ltl f1	{[](Rejection_purchase_requisition>=1 -> <>(Pay_bill>=1))}
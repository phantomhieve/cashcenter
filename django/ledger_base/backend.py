from ledger.models import LedgerData
def makeInstance(instance, request):
    new_instance = LedgerData(
            user         = request.user,
            l_r_no       = instance.l_r_no,
            l_r_date     = instance.l_r_date,
            bale_no      = instance.bale_no,
            supplier     = instance.supplier,
            location     = instance.location,
            item         = instance.item,
            pcs_mtr      = instance.pcs_mtr,
            price        = instance.price,
            weight       = instance.weight,
            frieght      = instance.frieght,
            transport    = instance.transport,
            delivery     = instance.delivery,
            reciept      = instance.reciept,
            remark       = instance.remark,
            status       = instance.status,
            hsn_code     = instance.hsn_code,
            bill_ammount = instance.bill_ammount,
            no_of_bale   = instance.no_of_bale
        )
    return new_instance

DefinitionBlock ("", "SSDT", 2, "OC", "XOSI", 0x00000001)
{
    Method (XOSI, 1, NotSerialized)
    {
        If (Arg0 == "Windows 2001")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2001 SP1")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2001 SP2")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2001 SP3")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2001.1")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2006")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2006 SP1")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2009")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2012")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2013")
        {
            Return (One)
        }
        ElseIf (Arg0 == "Windows 2015")
        {
            Return (One)
        }
        Return (Zero)
    }
}

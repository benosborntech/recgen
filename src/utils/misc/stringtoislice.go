package misc

func StringToISlice(slice []string) []interface{} {
	ifaceSlice := make([]interface{}, len(slice))
	for i, v := range slice {
		ifaceSlice[i] = v
	}

	return ifaceSlice
}

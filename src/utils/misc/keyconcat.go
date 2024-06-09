package misc

import "strings"

func KeyConcat(args ...string) string {
	return strings.Join(args, ":")
}
